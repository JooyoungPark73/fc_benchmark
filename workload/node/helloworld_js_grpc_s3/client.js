const grpc = require('@grpc/grpc-js');
const path = require('path');
const { program } = require('commander');
const protoLoader = require('@grpc/proto-loader');

const PROTO_PATH = path.join(__dirname, '../proto/busyspin.proto');

// Load proto file
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
  includeDirs: [path.join(__dirname, '../proto')]
});

const grpcObject = grpc.loadPackageDefinition(packageDefinition);
const ExecutorService = grpcObject.faas.Executor;

async function run(addr, port, name) {
  console.log("Will try to greet world ...");
  
  const client = new ExecutorService(
    `${addr}:${port}`,
    grpc.credentials.createInsecure()
  );

  const request = {
    message: name,
    runtimeInMilliSec: 0,
    memoryInMebiBytes: 0,
    ioSizeInBytes: 0
  };

  client.Execute(request, (error, response) => {
    if (error) {
      console.error(error);
      return;
    }
    console.log("Greeter client received: " + response.message);
  });
}

// Parse command line arguments
program
  .option('-a, --addr <addr>', 'Server IP address', '192.168.0.2')
  .option('-p, --port <port>', 'Server port number', '50051')
  .option('-n, --name <name>', 'Name to send', 'you')
  .parse();

const options = program.opts();
run(options.addr, options.port, options.name);
