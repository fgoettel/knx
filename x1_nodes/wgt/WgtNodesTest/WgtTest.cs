using System;
using System.Collections.Generic;
using System.Reflection;
using LogicModule.Nodes.TestHelper;
using LogicModule.ObjectModel;
using NUnit.Framework;

using Fabian_goettel_gmail_com.Logic.Wgt;
using System.Linq;

namespace WgtTest
{
    [TestFixture]
    public class WgtTest
    {
        private INodeContext context;
        private Wgt node;
        private Modbus mc;

        public WgtTest()
        {
            context = TestNodeContext.Create();
        }

        [SetUp]
        public void SetUp()
        {
            // Create node and trigger startup
            node = new Wgt(context);
            node.Startup();

            // Error should be false, error msg should be empty after startup
            Assert.IsFalse(node.ErrorBool.Value);
            Assert.AreEqual("", node.ErrorMsg.Value);

            // Check initial states
            // Inputs should be initialized
            Assert.IsTrue(node.Trigger.HasValue);
            Assert.IsTrue(node.TemperaturSollIn.HasValue);
            Assert.IsTrue(node.ZhFreigabeIn.HasValue);
            Assert.IsTrue(node.ZhStatusIn.HasValue);
            Assert.IsTrue(node.BetriebsartIn.HasValue);
            Assert.IsTrue(node.LuftleistungManuellIn.HasValue);
            Assert.IsTrue(node.StosslueftungIn.HasValue);
            Assert.IsTrue(node.LuftstufeManuellIn.HasValue);
            Assert.IsTrue(node.WpFreigabeHeizenIn.HasValue);
            Assert.IsTrue(node.WpFreigabeKuehlenIn.HasValue);
            // Inputs should have sensible values
            Assert.IsFalse(node.Trigger.Value);
            Assert.AreEqual(21.0, node.TemperaturSollIn.Value);
            Assert.IsFalse(node.ZhFreigabeIn.Value);
            Assert.IsFalse(node.ZhStatusIn.Value);
            Assert.AreEqual("Aus", node.BetriebsartIn.Value);
            Assert.AreEqual(70, node.LuftleistungManuellIn.Value);
            Assert.IsFalse(node.StosslueftungIn.Value);
            Assert.AreEqual("Aus", node.LuftstufeManuellIn.Value);
            Assert.IsFalse(node.WpFreigabeHeizenIn.Value);
            Assert.IsFalse(node.WpFreigabeKuehlenIn.Value);

            // Output values shouldn't be initialized
            Assert.IsFalse(node.TemperaturIstOut.HasValue);
            Assert.IsFalse(node.TemperaturSollOut.HasValue);
            Assert.IsFalse(node.ZhFreigabeOut.HasValue);
            Assert.IsFalse(node.ZhStatusOut.HasValue);
            Assert.IsFalse(node.TemperaturAussenOut.HasValue);
            Assert.IsFalse(node.BetriebsartOut.HasValue);
            Assert.IsFalse(node.LuftstufeAktuellOut.HasValue);
            Assert.IsFalse(node.LuftleistungManuellOut.HasValue);
            Assert.IsFalse(node.StosslueftungOut.HasValue);
            Assert.IsFalse(node.StosslueftungRestlaufzeitOut.HasValue);
            Assert.IsFalse(node.WpStatusOut.HasValue);
            Assert.IsFalse(node.FehlermeldungOut.HasValue);
            Assert.IsFalse(node.LuftstufeManuellOut.HasValue);
            Assert.IsFalse(node.BypassOut.HasValue);
            Assert.IsFalse(node.WpFreigabeHeizenOut.HasValue);
            Assert.IsFalse(node.WpFreigabeKuehlenOut.HasValue);
            Assert.IsFalse(node.MeldungOut.HasValue);

            this.InstrumentServer();
        }

        private void InstrumentServer()
        {
            // Instrument Modbus server
            // Use it to set values without a corresponding input
            this.mc = new Modbus("127.0.0.1", 502);

            // Set all register to the value of the address
            Type type = typeof(Addr);
            foreach (var p in type.GetFields(BindingFlags.Static | BindingFlags.Public))
            {
                short addr = (short)p.GetValue(type);
                this.mc.Write(addr, addr);

                // Rooms are additional
                if(p.Name.Contains("Raum0"))
                {
                    foreach (short rooms in Enumerable.Range(addr+1, 17))
                    {
                        this.mc.Write(rooms, rooms);
                    }
                }
            }

            // Empty all Meldungen
            foreach (KeyValuePair<string, short> entry in WgtEnums.Meldungen)
            {
                this.mc.Write(entry.Value, 0);
            }
            // Default all Enums to 0
            this.mc.Write(Addr.Bypass, 0);
            this.mc.Write(Addr.Fehlermeldung, 0);
            this.mc.Write(Addr.LuftstufeAktuell, 0);
            this.mc.Write(Addr.WpStatus, 0);
            // Bools to false
            this.mc.Write(Addr.WpFreigabeHeizen, 0);
            this.mc.Write(Addr.WpFreigabeKuehlen, 0);
        }

        [TearDown]
        public void TearDown()
        {
            this.node = null;
            this.mc = null;
        }


        /// <summary>
		/// Execute one cycle of the node and ensure no errors occured.
		/// </summary>
        private void Exec()
        {
            this.node.Execute();

            // No errors should have occured
            if (node.ErrorMsg.HasValue && node.ErrorMsg != "")
            {
                Console.WriteLine($"Error:\n\t{node.ErrorMsg.Value}");
            }
            Assert.IsTrue(node.ErrorBool.HasValue);
            Assert.IsFalse(node.ErrorBool.Value);
        }

        /// <summary>
		/// Helper function to execute a trigger and ensure no
		/// error occured.
		/// </summary>
        private void Trigger()
        {
            // Set trigger and execute
            this.node.Trigger.Value = true;
            this.Exec();
        }

        private short bound(short val, short lower, short upper)
        {
            if (val < lower)
            {
                val = lower;
            }
            if (val > upper)
            {
                val = upper;
            }
            return val;
        }

        private double bound(double val, short lower, short upper)
        {
            if (val < lower)
            {
                val = lower;
            }
            if (val > upper)
            {
                val = upper;
            }
            return val;
        }

        /// <summary>
		/// Execute the trigger - all values should've been set now.
        /// Ctrl+F '[Output(' should yield the same number as the asserts in this test.
		/// </summary>
        [Test]
        public void TriggerValueValid()
        {
            this.Trigger();

            // All outputs should have valid values
            Assert.IsTrue(node.TemperaturAussenOut.HasValue);
            Assert.IsTrue(node.BetriebsartOut.HasValue);
            Assert.IsTrue(node.FehlermeldungOut.HasValue);
            Assert.IsTrue(node.LuftstufeAktuellOut.HasValue);
            Assert.IsTrue(node.LuftleistungManuellOut.HasValue);
            Assert.IsTrue(node.StosslueftungOut.HasValue);
            Assert.IsTrue(node.StosslueftungRestlaufzeitOut.HasValue);
            Assert.IsTrue(node.TemperaturIstOut.HasValue);
            Assert.IsTrue(node.TemperaturSollOut.HasValue);
            Assert.IsTrue(node.WpStatusOut.HasValue);
            Assert.IsTrue(node.ZhFreigabeOut.HasValue);
            Assert.IsTrue(node.ZhStatusOut.HasValue);
            Assert.IsTrue(node.LuftstufeManuellOut.HasValue);
            Assert.IsTrue(node.BypassOut.HasValue);
            Assert.IsTrue(node.WpFreigabeHeizenOut.HasValue);
            Assert.IsTrue(node.WpFreigabeKuehlenOut.HasValue);
            Assert.IsTrue(node.ErrorBool.HasValue);
            Assert.IsTrue(node.ErrorMsg.HasValue);
            Assert.IsTrue(node.MeldungOut.HasValue);
        }

        /// <summary>
		/// Execute the trigger - all values should've been set now to the default values of the server.
        /// Ctrl+F '[Output(' should yield the same number as the asserts in this test.
        /// </summary>
        [Test]
        public void TriggerValueExpected()
        {
            this.Trigger();
            Assert.AreEqual(true, node.Trigger.Value);

            // All values should be their address (numbers)
            // Bool: true (if addr != 0)
            // Enum: see server
            // Temperature: Addr/10

            // Numbers
            Assert.AreEqual(Addr.StosslueftungRestlaufzeit, node.StosslueftungRestlaufzeitOut.Value);

            // Enum
            Assert.AreEqual("Aus", node.LuftstufeAktuellOut.Value);
            Assert.AreEqual("Kein Fehler", node.FehlermeldungOut.Value);
            Assert.AreEqual("Aus", node.WpStatusOut.Value);

            // Temperature
            Assert.AreEqual(Addr.Aussentemperatur / 10.0, node.TemperaturAussenOut.Value);
            Assert.AreEqual((Addr.Raum0TemperaturIst + node.RoomNr.Value)/10.0, node.TemperaturIstOut.Value);

            // Error checking just for completeness
            Assert.IsFalse(node.ErrorBool.Value);
            Assert.AreEqual("", node.ErrorMsg.Value);

            // Values with inputs are set to the corresponding input default value
            Assert.AreEqual(21.0, node.TemperaturSollIn.Value);
            Assert.AreEqual(false, node.ZhFreigabeIn.Value);
            Assert.AreEqual(false, node.ZhStatusIn.Value);
            Assert.AreEqual("Aus", node.BetriebsartIn.Value);
            Assert.AreEqual(70, node.LuftleistungManuellIn.Value);
            Assert.AreEqual(false, node.StosslueftungIn.Value);
            Assert.AreEqual("Aus", node.LuftstufeManuellIn.Value);
            Assert.AreEqual(false, node.WpFreigabeHeizenIn.Value);
            Assert.AreEqual(false, node.WpFreigabeKuehlenIn.Value);
            Assert.AreEqual("Keine Meldung", node.MeldungOut.Value);
        }

        [Test]
        public void TemperaturSoll()
        {
            var tests = new [] {9, 10, 12.3, 30, 31};

            foreach(var val in tests)
            {
                node.TemperaturSollIn.Value = val;
                this.Exec();

                var expected = this.bound(val, 10, 30);

                Assert.AreEqual(expected, node.TemperaturSollIn.Value);
                Assert.AreEqual(expected, node.TemperaturSollOut.Value);
            }
        }

        [Test]
        public void ZhFreigabe()
        {
            var tests = new [] {true, false, true};
            foreach(var val in tests)
            {
                node.ZhFreigabeIn.Value = val;
                this.Exec();
                Assert.AreEqual(val, node.ZhFreigabeIn.Value);
                Assert.AreEqual(val, node.ZhFreigabeOut.Value);
            }
        }

        [Test]
        public void ZhStatus()
        {
            var tests = new [] {true, false, true};
            foreach(var val in tests)
            {
                node.ZhStatusIn.Value = val;
                this.Exec();
                Assert.AreEqual(val, node.ZhStatusIn.Value);
                Assert.AreEqual(val, node.ZhStatusOut.Value);
            }
        }

        [Test]
        public void Betriebsart()
        {
            // Check all betriebsarten enums
            foreach (var val in WgtEnums.Betriebsarten.Keys)
            {
                node.BetriebsartIn.Value = val;
                this.Exec();
                Assert.AreEqual(val, node.BetriebsartOut.Value);
                Assert.AreEqual(val, node.BetriebsartIn.Value);
            }
        }


        [Test]
        public void LuftleistungManuell()
        {
            short[] tests = new short[] {-10, 0, 29, 30, 31, 70, 100, 101, 700};

            foreach(var val in tests)
            {
                node.LuftleistungManuellIn.Value = val;
                this.Exec();

                var expected = this.bound(val, 30, 100);
                Assert.AreEqual(expected, node.LuftleistungManuellIn.Value);
                Assert.AreEqual(expected, node.LuftleistungManuellOut.Value);
            }
        }

        [Test]
        public void Stosslueftung()
        {
            var tests = new [] {true, false, true};
            foreach(var val in tests)
            {
                node.StosslueftungIn.Value = val;
                this.Exec();
                Assert.AreEqual(val, node.StosslueftungIn.Value);
                Assert.AreEqual(val, node.StosslueftungOut.Value);
            }
        }

        [Test]
        public void LuftstufeManuell()
        {
            // Check all betriebsarten enums
            foreach (var val in WgtEnums.Luftstufe.Keys)
            {
                node.LuftstufeManuellIn.Value = val;
                this.Exec();
                Assert.AreEqual(val, node.LuftstufeManuellIn.Value);
                Assert.AreEqual(val, node.LuftstufeManuellOut.Value);
            }
        }

        [Test]
        public void WpFreigabeHeizen()
        {
            var tests = new [] {true, false, true};
            foreach(var val in tests)
            {
                node.WpFreigabeHeizenIn.Value = val;
                this.Exec();
                Assert.AreEqual(val, node.WpFreigabeHeizenIn.Value);
                Assert.AreEqual(val, node.WpFreigabeHeizenOut.Value);
            }
        }

        [Test]
        public void WpFreigabeKuehlen()
        {
            var tests = new[] {false, true, false};
            foreach(var val in tests)
            {
                node.WpFreigabeKuehlenIn.Value = val;
                this.Exec();
                Assert.AreEqual(val, node.WpFreigabeKuehlenIn.Value);
                Assert.AreEqual(val, node.WpFreigabeKuehlenOut.Value);
            }
        }
    }
}