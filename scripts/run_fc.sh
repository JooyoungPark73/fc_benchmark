TAP_DEV="tap0"
TAP_IP="192.168.0.1"
MASK_SHORT="/30"
TAP_MAC="52:82:10:11:19:3b"

# Setup network interface
sudo ip link del "$TAP_DEV" 2> /dev/null || true
sudo ip tuntap add dev "$TAP_DEV" mode tap
sudo ip link set dev "$TAP_DEV" address "$TAP_MAC"  # Set the MAC address
sudo ip addr add "${TAP_IP}${MASK_SHORT}" dev "$TAP_DEV"
sudo ip link set dev "$TAP_DEV" up

# Enable ip forwarding
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

HOST_IFACE="eno1"

# Set up microVM internet access
sudo iptables -t nat -D POSTROUTING -o "$HOST_IFACE" -j MASQUERADE || true
sudo iptables -D FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT \
    || true
sudo iptables -D FORWARD -i tap0 -o "$HOST_IFACE" -j ACCEPT || true
sudo iptables -t nat -A POSTROUTING -o "$HOST_IFACE" -j MASQUERADE
sudo iptables -I FORWARD 1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
sudo iptables -I FORWARD 1 -i tap0 -o "$HOST_IFACE" -j ACCEPT

API_SOCKET="/tmp/firecracker.socket"
LOGFILE="./firecracker.log"

# Create log file
touch $LOGFILE

# Set log file
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"log_path\": \"${LOGFILE}\",
        \"level\": \"Debug\",
        \"show_level\": true,
        \"show_log_origin\": true
    }" \
    "http://localhost/logger"

###

# Set machine configuration
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"vcpu_count\": 2,
        \"mem_size_mib\": 1024,
        \"track_dirty_pages\": true
    }" \
    "http://localhost/machine-config"

###

KERNEL="./ubuntu/vmlinux-6.1.102"
KERNEL_BOOT_ARGS="console=ttyS0 reboot=k panic=1 pci=off"

ARCH=$(uname -m)

if [ ${ARCH} = "aarch64" ]; then
    KERNEL_BOOT_ARGS="keep_bootcon ${KERNEL_BOOT_ARGS}"
fi

# Set boot source
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"kernel_image_path\": \"${KERNEL}\",
        \"boot_args\": \"${KERNEL_BOOT_ARGS}\"
    }" \
    "http://localhost/boot-source"

ROOTFS="./ubuntu/ubuntu-22.04.ext4"

# Set vsock
VSOCK_DIR="/tmp/v.sock"
sudo rm ${VSOCK_DIR}
curl --unix-socket "${API_SOCKET}" -i \
    -X PUT 'http://localhost/vsock' \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        "guest_cid": 3,
        "uds_path": "'${VSOCK_DIR}'"
    }'

# Set rootfs
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"drive_id\": \"rootfs\",
        \"path_on_host\": \"${ROOTFS}\",
        \"is_root_device\": true,
        \"is_read_only\": false
    }" \
    "http://localhost/drives/rootfs"

# The IP address of a guest is derived from its MAC address with
# `fcnet-setup.sh`, this has been pre-configured in the guest rootfs. It is
# important that `TAP_IP` and `FC_MAC` match this.
# FC_MAC="06:00:AC:10:00:02"
FC_MAC="06:00:C0:A8:00:02" # 192.168.0.2

# Set network interface
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"iface_id\": \"net1\",
        \"guest_mac\": \"$FC_MAC\",
        \"host_dev_name\": \"$TAP_DEV\"
    }" \
    "http://localhost/network-interfaces/net1"

# API requests are handled asynchronously, it is important the configuration is
# set, before `InstanceStart`.
sleep 0.015s

# Start microVM
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"action_type\": \"InstanceStart\"
    }" \
    "http://localhost/actions"

# API requests are handled asynchronously, it is important the microVM has been
# started before we attempt to SSH into it.
sleep 5s

# Setup internet access in the guest
ssh -i ./ubuntu/ubuntu-22.04.id_rsa root@192.168.0.2  "ip route add default via 192.168.0.1 dev eth0"

# Setup DNS resolution in the guest
ssh -i ./ubuntu/ubuntu-22.04.id_rsa root@192.168.0.2  "echo 'nameserver 8.8.8.8' > /etc/resolv.conf"

# Create apt file 
# ssh -i ./ubuntu/ubuntu-22.04.id_rsa root@192.168.0.2  "touch /var/lib/dpkg/status"

# SSH into the microVM
# ssh -i ./ubuntu/ubuntu-22.04.id_rsa root@192.168.0.2

# Use `root` for both the login and password.
# Run `reboot` to exit.