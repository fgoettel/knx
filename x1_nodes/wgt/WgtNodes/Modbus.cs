// Author: Fabian Göttel
// Copyright (c) Fabian  Göttel
// See LICENSE in the project root for license informa

namespace Fabian_goettel_gmail_com.Logic.Wgt
{
    using System;
    using System.Collections.Generic;
    using System.Net.NetworkInformation;
    using System.Net.Sockets;
    using System.Threading;

    /// <summary>
    /// Overly simplified Modbus implementation that has only one purpose:
    /// read and write information to a Schwörer WGT.
    ///
    /// Only the ReadHoldingregister and WriteMultipleRegisters
    /// are implemented to read/write exactly one word (16 bit).
    /// </summary>
    public class Modbus
    {
        // Statics and consts
        private const short SizeHeader = 6;
        private const short SizePayloadMin = 6;
        private static HashSet<short> tids = new HashSet<short>();

        // Configuration
        private readonly int port;
        private readonly string ip;
        private readonly int timeoutMs;
        private readonly bool isLittleEndian;

        // Internals
        private TcpClient client;
        private NetworkStream stream;

        /// <summary>
        /// Instantiate Modbus with defaul timeout of 60 seconds.
        /// </summary>
        /// <param name="ip"></param>
        /// <param name="port"></param>
        /// <param name="timeout"></param>
        public Modbus(string ip, int port, int timeout = 60000)
        {
            this.ip = ip;
            this.port = port;
            this.timeoutMs = timeout;
            this.isLittleEndian = BitConverter.IsLittleEndian;
        }

        ~Modbus()
        {
            try
            {
                this.Disconnect();
            }
            catch (System.Exception)
            {
            }
        }

        /// <summary>
        /// Connected status of this Instance mapped to TcpClient.
        /// </summary>
        public bool Connected => this.client?.Connected ?? false;

        /// <summary>
        /// Initialize tcp client and stream.
        /// </summary>
        private void Init()
        {
            this.client = new TcpClient(this.ip, this.port);
            this.stream = this.client.GetStream();
        }

        /// <summary>
        /// Write a given value to the given address
        /// </summary>
        /// <param name="address"></param>
        /// <param name="value"></param>
        public void Write(short address, short value)
        {
            // Esnure that we're connected.
            this.InitOrFail();

            // Create and execute transaction
            short tid = Modbus.TidGet();
            var header = this.CreateModbusHeaderWrite(address, value, tid);
            this.WriteToStream(header);
            const short responseArrayLength = 12;
            var response = this.ReadFromStream(responseArrayLength);
            Modbus.TidReturn(tid);

            // Verify request by comparing the sent items with the response.
            // 1. copy the first responseArrayLength bytes from the request header
            // 2. fix the now adapted length
            byte[] tmp = new byte[responseArrayLength];
            Array.Copy(header, tmp, responseArrayLength);
            tmp[5] = (byte)(tmp.Length - Modbus.SizeHeader);

            // The shortened request and the response should be equal.
            if (!ByteArrayEqual(tmp, response))
            {
                throw new Exception("Write response invalid.");
            }
        }

        /// <summary>
        /// Read value from WGT
        /// </summary>
        /// <param name="address">Address of the register.</param>
        /// <returns>Read data</returns>
        public short Read(short address)
        {
            // Ensure that we are in a good to go shape.
            this.InitOrFail();

            // Create and execute transaction
            short tid = Modbus.TidGet();
            var header = this.CreateModbusHeaderRead(address: address, transactionId: tid);
            this.WriteToStream(header);
            const short responseArrayLength = 11;
            short response = this.ReadValue(responseArrayLength);
            Modbus.TidReturn(tid);

            // Todo: compare header / tid
            return response;
        }

        /// <summary>
        /// Update a value.
        /// I.e. first perform a write and then a read.
        /// </summary>
        /// <param name="address"></param>
        /// <param name="value"></param>
        /// <returns></returns>
        public short Update(short address, short value)
        {
            this.Write(address, value);
            return this.Read(address);
        }

        private static short TidGet()
        {
            // TODO: Cover the case of running out of transaction ids.
            short tid;
            for (tid = 0; tid < short.MaxValue; tid++)
            {
                if (!Modbus.tids.Contains(tid))
                {
                    break;
                }
            }

            tids.Add(tid);
            return tid;
        }

        private static void TidReturn(short tid)
        {
            Modbus.tids.Remove(tid);
            return;
        }

        private static bool ByteArrayEqual(byte[] a, byte[] b)
        {
            if (a.Length != b.Length)
            {
                return false;
            }

            for (int i = 0; i < a.Length; i++)
            {
                if (a[i] != b[i])
                {
                    return false;
                }
            }

            return true;
        }

        private void InitOrFail()
        {
            // If we have created a client initially and are connected everything is alright
            if (this.client != null && this.Connected)
            {
                return;
            }

            // Clean state
            this.Disconnect();

            // Might fail
            this.Init();
        }

        private void Disconnect()
        {
            if (this.stream != null)
            {
                this.stream.Close();
            }
            if (this.client != null)
            {
                this.client.Close();
            }
        }

        private short ReadValue(short totalSize)
        {
            byte[] buffer = this.ReadFromStream(totalSize);

            // Extract value from byte array response
            // TODO: Validate if this is actually true or if the complete buffer should be reversed.
            byte[] valueBytes = { buffer[9], buffer[10] };
            if (this.isLittleEndian)
            {
                Array.Reverse(valueBytes);
            }

            return BitConverter.ToInt16(valueBytes, 0);
        }

        private byte[] ReadFromStream(short totalSize)
        {
            var buffer = new byte[totalSize];

            var idx = 0;
            var remainder = Convert.ToInt32(totalSize);

            // Read from network
            while (remainder > 0)
            {
                int readBytes = 0;
                using (var cancellationTokenSource = new CancellationTokenSource(this.timeoutMs))
                {
                    using (cancellationTokenSource.Token.Register(() => this.stream.Close()))
                    {
                        readBytes = this.stream.Read(buffer, idx, remainder);
                    }
                }

                remainder -= readBytes;
                idx += readBytes;

                if (readBytes == 0)
                {
                    throw new Exception("Error while reading from buffer.");
                }
            }

            return buffer;
        }

        private void WriteToStream(byte[] msg)
        {
            using (var cancellationTokenSource = new CancellationTokenSource(this.timeoutMs))
            {
                using (cancellationTokenSource.Token.Register(() => this.stream.Close()))
                {
                    this.stream.Write(msg, 0, msg.Length);
                }
            }
        }

        private byte[] CreateModbusHeader(
            short address, short transactionId, byte function, short length)
        {
            // Create header with minimum length of 6+6
            if (length < Modbus.SizePayloadMin)
            {
                length = Modbus.SizePayloadMin;
            }

            var header = new byte[Modbus.SizeHeader + length];

            // All to byte
            var registerCountB = BitConverter.GetBytes((short)1);
            var addressB = BitConverter.GetBytes(address);
            var transactionIdB = BitConverter.GetBytes(transactionId);
            var lengthB = BitConverter.GetBytes(length);

            // All data / addresses, etc in Modbus are big endian
            if (this.isLittleEndian)
            {
                Array.Reverse(addressB);
                Array.Reverse(transactionIdB);
                Array.Reverse(registerCountB);
                Array.Reverse(lengthB);
            }

            // Header Description
            // 0 - 1  Transaction identifier - sync between messages of server and client
            // 2 - 3  Protocol identifier - 0 for Tcp
            // 4 - 5  Length field - number of remaining bytes in this frame
            //     6  Unit identifier - slave address (255 if not used)
            //        Header End
            //     7  Function code (3 - read holding register, 16 write multiple register)
            header[0] = transactionIdB[0];
            header[1] = transactionIdB[1];
            header[2] = 0;
            header[3] = 0;
            header[4] = lengthB[0];
            header[5] = lengthB[1];
            header[6] = 0;
            header[7] = function;
            header[8] = addressB[0];
            header[9] = addressB[1];
            header[10] = registerCountB[0];
            header[11] = registerCountB[1];

            return header;
        }

         private byte[] CreateModbusHeaderRead(short address, short transactionId)
        {
            byte function = 3;
            short length = 6;
            return this.CreateModbusHeader(
                address: address,
                transactionId: transactionId,
                function: function,
                length: length);
        }

        private byte[] CreateModbusHeaderWrite(short address, short value, short transactionId)
        {
            const byte FunctionId = 16;
            short length = 9;

            var header = this.CreateModbusHeader(
                address: address,
                transactionId: transactionId,
                function: FunctionId,
                length: length);

            // All data / addresses, etc in Modbus are big endian
            var value_bytes = BitConverter.GetBytes(value);
            if (this.isLittleEndian)
            {
                Array.Reverse(value_bytes);
            }

            header[12] = 2;   // byte count
            header[13] = value_bytes[0];
            header[14] = value_bytes[1];

            return header;
        }
    }
}
