using System;
using NUnit.Framework;

using Fabian_goettel_gmail_com.Logic.Wgt;

namespace ModbusTest
{
    [TestFixture]
    public class ModbusTest
    {
        Modbus client;
        const string ip = "127.0.0.1";
        const int port = 5020;

        [SetUp]
        public void SetUp()
        {
            this.client = new Modbus(ModbusTest.ip, ModbusTest.port);
        }


        [Test]
        public void Read()
        {
            var retVal = this.client.Read(Addr.Aussentemperatur);
            Assert.IsInstanceOf(typeof(short), retVal);
        }

        [Test]
        public void Write()
        {
            short value = 42;
            short address = Addr.BetriebsstundenEWT;
            this.client.Write(address, value);
            var retVal = this.client.Read(address);
            Assert.AreEqual(value, retVal);
        }

        [Test]
        public void Update()
        {
            short address = Addr.Stosslueftung;

            var initVal = this.client.Read(address);
            var value =  (short)(initVal + 1);
            Assert.AreNotEqual(value, initVal);

            var retVal = this.client.Update(address, value);
            Assert.AreEqual(value, retVal);
        }
    }
}
