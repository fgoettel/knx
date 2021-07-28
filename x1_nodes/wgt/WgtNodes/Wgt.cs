// Author: Fabian Göttel
// Copyright (c) Fabian  Göttel
// See LICENSE in the project root for license informa

namespace Fabian_goettel_gmail_com.Logic.Wgt
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    using LogicModule.Nodes.Helpers;
    using LogicModule.ObjectModel;
    using LogicModule.ObjectModel.TypeSystem;

    /// <summary>
    /// Update WGT / Ventilation system properties.
    /// </summary>
    public class Wgt : LogicNodeBase
    {
        private const int port = 502;
        private readonly ITypeService typeService;
        private Modbus modbusClient;

        public Wgt(INodeContext context)
          : base(context)
        {
            // Default structure
            context.ThrowIfNull("context");
            this.typeService = context.GetService<ITypeService>();

            // Parameter
            this.Ip = this.typeService.CreateString(PortTypes.String, "Ip", "127.0.0.1");
            this.RoomNr = this.typeService.CreateInt(PortTypes.Integer, "Raum Nummer", 1);
            this.RoomNr.MinValue = 1;
            this.RoomNr.MaxValue = 17;

            // Inputs
            // All should have a sensible default
            this.Trigger = this.typeService.CreateBool(PortTypes.Binary, "Trigger", false);
            this.TemperaturSollIn = this.typeService.CreateDouble(PortTypes.Temperature, "Solltemperatur In", 21.0, "°C");
            this.TemperaturSollIn.MinValue = 10;
            this.TemperaturSollIn.MaxValue = 30;
            this.ZhFreigabeIn = this.typeService.CreateBool(PortTypes.Bool, "ZH Freigabe In", false);
            this.ZhStatusIn = this.typeService.CreateBool(PortTypes.Bool, "ZH Status In", false);
            this.BetriebsartIn = this.typeService.CreateEnum(
                typeName: "BETRIEBSART",
                name: "Betriebsart In",
                allowedValues: WgtEnums.Betriebsarten.Keys.ToArray(),
                defaultValue: "Aus");
            this.LuftleistungManuellIn = this.typeService.CreateInt(PortTypes.Integer, "Luftleistung Manuell In", 70);
            this.LuftleistungManuellIn.MinValue = 30;
            this.LuftleistungManuellIn.MaxValue = 100;
            this.StosslueftungIn = this.typeService.CreateBool(PortTypes.Bool, "Stosslueftung In", false);
            this.LuftstufeManuellIn = this.typeService.CreateEnum(
                typeName: "LUFTSTUFE",
                name: "Manuelle Luftstufe In",
                allowedValues: WgtEnums.Luftstufe.Keys.ToArray(),
                defaultValue: "Aus");
            this.WpFreigabeHeizenIn = this.typeService.CreateBool(PortTypes.Bool, "WP Freigabe Heizen In", false);
            this.WpFreigabeKuehlenIn = this.typeService.CreateBool(PortTypes.Bool, "WP Freigabe Kuehlen In", false);

            // Outputs
            this.ErrorBool = this.typeService.CreateBool(PortTypes.Bool, "Error Bool");
            this.ErrorMsg = this.typeService.CreateString(PortTypes.String, "Error Message");
            this.TemperaturIstOut = this.typeService.CreateDouble(PortTypes.Temperature, "Temperatur Ist Out");
            this.TemperaturSollOut = this.typeService.CreateDouble(PortTypes.Temperature, "Temperatur Soll Out");
            this.ZhFreigabeOut = this.typeService.CreateBool(PortTypes.Bool, "ZH Freigabe Out");
            this.ZhStatusOut = this.typeService.CreateBool(PortTypes.Bool, "ZH Status Out");
            this.TemperaturAussenOut = this.typeService.CreateDouble(PortTypes.Temperature, "Aussentemperatur Out");
            this.BetriebsartOut = this.typeService.CreateEnum(
                typeName: "BETRIEBSART",
                name: "Betriebsart Out");
            this.LuftstufeAktuellOut = this.typeService.CreateEnum(
                typeName: "LUFTSTUFE",
                name: "Luftstufe Aktuell Out");
            this.LuftleistungManuellOut = this.typeService.CreateInt(PortTypes.Integer, "Luftleistung Manuell Out");
            this.StosslueftungOut = this.typeService.CreateBool(PortTypes.Bool, "Stosslueftung Out");
            this.StosslueftungRestlaufzeitOut = this.typeService.CreateInt(PortTypes.Integer, "Stosslueftung Restlaufzeit Out");
            this.WpStatusOut = this.typeService.CreateEnum(
                typeName: "WPSTATUS",
                name: "WP Status Out",
                allowedValues: WgtEnums.WaermepumpeStatus.Keys.ToArray());
            this.FehlermeldungOut = this.typeService.CreateEnum(
                typeName: "FEHLERMELDUNG",
                name: "Fehlermeldung Out",
                allowedValues: WgtEnums.Fehlermeldung.Keys.ToArray());
            this.LuftstufeManuellOut = this.typeService.CreateEnum(
                typeName: "LUFTSTUFE",
                name: "Manuelle Luftstufe Out");
            this.BypassOut = this.typeService.CreateEnum(
                typeName: "BYPASS",
                name: "Bypass Out",
                allowedValues: WgtEnums.Bypass.Keys.ToArray());
            this.WpFreigabeHeizenOut = this.typeService.CreateBool(PortTypes.Bool, "WP Freigabe Heizen Out");
            this.WpFreigabeKuehlenOut = this.typeService.CreateBool(PortTypes.Bool, "WP Freigabe Kuehlen Out");
            this.MeldungOut = this.typeService.CreateString(PortTypes.String, "Meldung Out");
        }

        [Parameter(DisplayOrder = 1, IsRequired = true)]
        public StringValueObject Ip { get; private set; }

        [Parameter(DisplayOrder = 2, IsRequired = true)]
        public IntValueObject RoomNr { get; private set; }

        [Input(DisplayOrder = 3, IsRequired = true)]
        public BoolValueObject Trigger { get; private set; }

        [Input(DisplayOrder = 13, IsRequired = false)]
        public DoubleValueObject TemperaturSollIn { get; private set; }

        [Input(DisplayOrder = 14, IsRequired = false)]
        public BoolValueObject ZhFreigabeIn { get; private set; }

        [Input(DisplayOrder = 15, IsRequired = false)]
        public BoolValueObject ZhStatusIn { get; private set; }

        [Input(DisplayOrder = 16, IsRequired = false)]
        public EnumValueObject BetriebsartIn { get; private set; }

        [Input(DisplayOrder = 17, IsRequired = false)]
        public BoolValueObject StosslueftungIn { get; private set; }

        [Input(DisplayOrder = 19, IsRequired = false)]
        public IntValueObject LuftleistungManuellIn { get; private set; }

        [Input(DisplayOrder = 21, IsRequired = false)]
        public EnumValueObject LuftstufeManuellIn { get; private set; }

        [Input(DisplayOrder = 24, IsRequired = false)]
        public BoolValueObject WpFreigabeHeizenIn { get; private set; }

        [Input(DisplayOrder = 25, IsRequired = false)]
        public BoolValueObject WpFreigabeKuehlenIn { get; private set; }

        [Output(DisplayOrder = 1, IsRequired = true)]
        public BoolValueObject ErrorBool { get; private set; }

        [Output(DisplayOrder = 2, IsRequired = true)]
        public StringValueObject ErrorMsg { get; private set; }

        [Output(DisplayOrder = 3, IsRequired = false)]
        public EnumValueObject FehlermeldungOut { get; private set; }

        [Output(DisplayOrder = 11, IsRequired = false)]
        public DoubleValueObject TemperaturAussenOut { get; private set; }

        [Output(DisplayOrder = 12, IsRequired = false)]
        public DoubleValueObject TemperaturIstOut { get; private set; }

        [Output(DisplayOrder = 13, IsRequired = false)]
        public DoubleValueObject TemperaturSollOut { get; private set; }

        [Output(DisplayOrder = 14, IsRequired = false)]
        public BoolValueObject ZhFreigabeOut { get; private set; }

        [Output(DisplayOrder = 15, IsRequired = false)]
        public BoolValueObject ZhStatusOut { get; private set; }

        [Output(DisplayOrder = 16, IsRequired = false)]
        public EnumValueObject BetriebsartOut { get; private set; }

        [Output(DisplayOrder = 17, IsRequired = false)]
        public BoolValueObject StosslueftungOut { get; private set; }

        [Output(DisplayOrder = 18, IsRequired = false)]
        public IntValueObject StosslueftungRestlaufzeitOut { get; private set; }

        [Output(DisplayOrder = 19, IsRequired = false)]
        public IntValueObject LuftleistungManuellOut { get; private set; }

        [Output(DisplayOrder = 20, IsRequired = false)]
        public EnumValueObject LuftstufeAktuellOut { get; private set; }

        [Output(DisplayOrder = 21, IsRequired = false)]
        public EnumValueObject LuftstufeManuellOut { get; private set; }

        [Output(DisplayOrder = 22, IsRequired = false)]
        public EnumValueObject BypassOut { get; private set; }

        [Output(DisplayOrder = 23, IsRequired = false)]
        public EnumValueObject WpStatusOut { get; private set; }

        [Output(DisplayOrder = 24, IsRequired = false)]
        public BoolValueObject WpFreigabeHeizenOut { get; private set; }

        [Output(DisplayOrder = 25, IsRequired = false)]
        public BoolValueObject WpFreigabeKuehlenOut { get; private set; }

        [Output(DisplayOrder = 28, IsRequired = false)]
        public StringValueObject MeldungOut { get; private set; }

        /// <summary>
        ///  Initially executed (i.e. during startup on the X1).
        /// </summary>
        public sealed override void Startup()
        {
            // Assume everything will be alright
            this.ErrorBool.Value = false;
            this.ErrorMsg.Value = string.Empty;

            try
            {
                this.modbusClient = new Modbus(this.Ip, Wgt.port);
            }
            catch (Exception e)
            {
                this.ErrorBool.Value = true;
                this.ErrorMsg.Value = e.Message;
            }
        }

        public sealed override void Execute()
        {
            this.ErrorBool.Value = false;
            try
            {
                // Bools
                if (this.ZhFreigabeIn.HasValue && this.ZhFreigabeIn.WasSet)
                {
                    short addrZhFreigabe = (short)(Addr.Raum0ZusatzheizungFreigabe + this.RoomNr.Value);
                    this.ZhFreigabeOut.Value = this.bUpdate(addrZhFreigabe, this.ZhFreigabeIn);
                }
                if (this.ZhStatusIn.HasValue && this.ZhStatusIn.WasSet)
                {
                    short addrZhStatus = (short)(Addr.Raum0ZusatzheizungStatus + this.RoomNr.Value);
                    this.ZhStatusOut.Value = this.bUpdate(addrZhStatus, this.ZhStatusIn);
                }
                if (this.StosslueftungIn.HasValue && this.StosslueftungIn.WasSet)
                {
                    this.StosslueftungOut.Value = this.bUpdate(Addr.Stosslueftung, this.StosslueftungIn);
                    this.StosslueftungRestlaufzeitOut.Value = this.sRead(Addr.StosslueftungRestlaufzeit);
                }
                if (this.WpFreigabeHeizenIn.HasValue && this.WpFreigabeHeizenIn.WasSet)
                {
                    this.WpFreigabeHeizenOut.Value = this.bUpdate(Addr.WpFreigabeHeizen, this.WpFreigabeHeizenIn);
                }
                if (this.WpFreigabeKuehlenIn.HasValue && this.WpFreigabeKuehlenIn.WasSet)
                {
                    this.WpFreigabeKuehlenOut.Value = this.bUpdate(Addr.WpFreigabeKuehlen, this.WpFreigabeKuehlenIn);
                }

                // Temperature
                if (this.TemperaturSollIn.HasValue && this.TemperaturSollIn.WasSet)
                {
                    short addrTemperaturSoll = (short)(Addr.Raum0TemperaturSoll + this.RoomNr.Value);
                    this.TemperaturSollOut.Value = this.tUpdate(addrTemperaturSoll, this.TemperaturSollIn);
                }

                // Integer
                if (this.LuftleistungManuellIn.HasValue && this.LuftleistungManuellIn.WasSet)
                {
                    this.LuftleistungManuellOut.Value = this.iUpdate(Addr.LuftleistungManuell, this.LuftleistungManuellIn);
                }

                // Enum
                if (this.BetriebsartIn.HasValue && this.BetriebsartIn.WasSet)
                {
                    this.BetriebsartOut.Value = this.eUpdate(Addr.Betriebsart, this.BetriebsartIn, WgtEnums.Betriebsarten);
                }
                if (this.LuftstufeManuellIn.HasValue && this.LuftstufeManuellIn.WasSet)
                {
                    this.LuftstufeManuellOut.Value = this.eUpdate(Addr.LuftstufeManuell, this.LuftstufeManuellIn, WgtEnums.Luftstufe);
                }

                // If the trigger was set, read all values
                if (this.Trigger.WasSet && this.Trigger.Value)
                {
                    this.ReadAll();
                }
            }
            catch (Exception e)
            {
                this.ErrorBool.Value = true;
                this.ErrorMsg.Value = e.Message;
            }
        }

        /// <summary>
        /// Validate the IP format.
        /// </summary>
        /// <param name="language">Language of the (potential) error message.</param>
        /// <returns>Validation result.</returns>
        public sealed override ValidationResult Validate(string language)
        {
            // TODO: Validate IP without system.net
            return base.Validate(language);
        }

        /// <summary>
        /// Update all properties.
        /// </summary>
        private void ReadAll()
        {
            // Bools
            short addrZhFreigabe = (short)(Addr.Raum0ZusatzheizungFreigabe + this.RoomNr.Value);
            this.ZhFreigabeOut.Value = this.bRead(addrZhFreigabe);
            short addrZhStatus = (short)(Addr.Raum0ZusatzheizungStatus + this.RoomNr.Value);
            this.ZhStatusOut.Value = this.bRead(addrZhStatus);
            this.StosslueftungOut.Value = this.bRead(Addr.Stosslueftung);
            this.WpFreigabeHeizenOut.Value = this.bRead(Addr.WpFreigabeHeizen);
            this.WpFreigabeKuehlenOut.Value = this.bRead(Addr.WpFreigabeKuehlen);

            // Temperature
            short addrTemperaturIst = (short)(Addr.Raum0TemperaturIst + this.RoomNr.Value);
            this.TemperaturIstOut.Value = this.tRead(addrTemperaturIst);
            short addrTemperaturSoll = (short)(Addr.Raum0TemperaturSoll + this.RoomNr.Value);
            this.TemperaturSollOut.Value = this.tRead(addrTemperaturSoll);
            this.TemperaturAussenOut.Value = this.tRead(Addr.Aussentemperatur);

            // Integer
            this.LuftleistungManuellOut.Value = this.sRead(Addr.LuftleistungManuell);
            this.StosslueftungRestlaufzeitOut.Value = this.sRead(Addr.StosslueftungRestlaufzeit);

            // Enum
            this.BetriebsartOut.Value = this.eRead(Addr.Betriebsart, WgtEnums.Betriebsarten);
            this.WpStatusOut.Value = this.eRead(Addr.WpStatus, WgtEnums.WaermepumpeStatus);
            this.FehlermeldungOut.Value = this.eRead(Addr.Fehlermeldung, WgtEnums.Fehlermeldung);
            this.LuftstufeManuellOut.Value = this.eRead(Addr.LuftstufeManuell, WgtEnums.Luftstufe);
            this.LuftstufeAktuellOut.Value = this.eRead(Addr.LuftstufeAktuell, WgtEnums.Luftstufe);
            this.BypassOut.Value = this.eRead(Addr.Bypass, WgtEnums.Bypass);

            // String (special methods)
            this.MeldungOut.Value = this.MeldungRead();
        }

        private short sRead(short address)
        {
            return this.modbusClient.Read(address);
        }

        private short sUpdate(short address, short value)
        {
            return this.modbusClient.Update(address, value);
        }

        private int iUpdate(short address, int value)
        {
            return this.sUpdate(address, (short)value);
        }

        private bool bRead(short address)
        {
            return this.sRead(address: address) != 0;
        }

        private bool bUpdate(short address, bool bValue)
        {
            short value = bValue ? (short)1 : (short)0;
            return this.sUpdate(address, value) != 0;
        }

        private string eRead(short address, Dictionary<string, short> mapping)
        {
            short tmp = this.sRead(address);
            return mapping.FirstOrDefault(x => x.Value == tmp).Key;
        }

        private string eUpdate(short address, string sValue, Dictionary<string, short> mapping)
        {
            short value = mapping[sValue];
            short tmp = this.sUpdate(address, value);
            return mapping.FirstOrDefault(x => x.Value == tmp).Key;
        }

        private double tRead(short address)
        {
            return this.sRead(address: address) / 10.0;
        }

        private double tUpdate(short address, double value)
        {
            return this.sUpdate(address, (short)(value * 10)) / 10.0;
        }

        private string MeldungRead()
        {
            var meldungen = new List<string>();
            // Check all Meldung addresses
            foreach (KeyValuePair<string, short> entry in WgtEnums.Meldungen)
            {
                if (bRead(entry.Value))
                {
                    meldungen.Add(entry.Key);
                }
            }

            var meldung = string.Empty;
            if (meldungen.Count() > 0)
            {
                meldung = string.Join(" | ", meldungen);
            }
            else
            {
                meldung = "Keine Meldung";
            }
            return meldung;
        }
    }
}
