const grpc = require('@grpc/grpc-js');
const path = require('path');
const { program } = require('commander');
const protoLoader = require('@grpc/proto-loader');
const { S3Client, GetObjectCommand, PutObjectCommand } = require('@aws-sdk/client-s3');

const PROTO_PATH = path.join(__dirname, '../proto/busyspin.proto');

// Load proto file with correct package name
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

class Executor {
  async Execute(call, callback) {
    const msg = `Hello, ${call.request.message}!`;
    const s3Client = new S3Client({});

    try {
      const getCommand = new GetObjectCommand({
        Bucket: 'nexus-benchmark-payload',
        Key: 'input_payload/auth/auth_input.txt'
      });
      const response = await s3Client.send(getCommand);
      const bodyContents = await response.Body.transformToString();

      const putCommand = new PutObjectCommand({
        Bucket: 'nexus-benchmark-payload',
        Key: 'output_payload/auth/auth_output.txt',
        Body: bodyContents
      });
      await s3Client.send(putCommand);

      callback(null, {
        message: msg,
        durationInMicroSec: 0,
        memoryUsageInKb: 0, 
        ioTimeInMicroSec: 0
      });

    } catch (error) {
      console.error(`Error: ${error}`);
      callback(null, {
        message: "Error",
        durationInMicroSec: 0,
        memoryUsageInKb: 0,
        ioTimeInMicroSec: 0
      });
    }
  }
}

function serve(addr, port) {
  const server = new grpc.Server();
  
  if (!ExecutorService || !ExecutorService.service) {
    throw new Error('ExecutorService not found in proto definition');
  }

  server.addService(ExecutorService.service, {
    Execute: (call, callback) => new Executor().Execute(call, callback)
  });
  
  server.bindAsync(`${addr}:${port}`, grpc.ServerCredentials.createInsecure(), (err, port) => {
    if (err) {
      console.error(err);
      return;
    }
    server.start();
    console.log(`Server started, listening on ${port}`);
  });
}

program
  .option('-a, --addr <addr>', 'Server IP address', '192.168.0.2')
  .option('-p, --port <port>', 'Server port number', '50051')
  .parse();

const options = program.opts();
serve(options.addr, options.port);
