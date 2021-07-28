using System;
using System.Reflection;
using System.Linq;
using NUnit.Framework;

using Fabian_goettel_gmail_com.Logic.Wgt;

namespace AddressTest
{
    [TestFixture]
    public class AddressTest
    {
        [Test]
        public void EnsureUniqueness()
        {
            var addresses = new System.Collections.Generic.List<short>();
            Type type = typeof(Addr);
            foreach (var p in type.GetFields(BindingFlags.Static | BindingFlags.Public))
            {
                addresses.Add((short)p.GetValue(type));
            }
            // Ensure that the distinct set is as large as the complete list
            Assert.AreEqual(addresses.Distinct().Count(), addresses.Count());
        }
    }
}
