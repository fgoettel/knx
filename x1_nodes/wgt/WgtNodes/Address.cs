// Author: Fabian Göttel
// Copyright (c) Fabian  Göttel
// See LICENSE in the project root for license information.

namespace Fabian_goettel_gmail_com.Logic.Wgt
{
    /// <summary>
    /// Exchange WGT address.
    /// </summary>
    public static class Addr
    {
        // 1xx
        public const short Betriebsart = 100;
        public const short LuftstufeManuell = 101;
        public const short LuftstufeAktuell = 102;
        public const short LuftleistungManuell = 103;
        public const short Stosslueftung = 111;
        public const short StosslueftungRestlaufzeit = 112;
        public const short WpStatus = 114;
        public const short Bypass = 123;

        // 2xx
        public const short Aussentemperatur = 209;
        public const short WpFreigabeHeizen = 231;
        public const short WpFreigabeKuehlen = 232;
        public const short Fehlermeldung = 240;

        public const short MeldungDruckwächter = 242;
        public const short MeldungEVUSperre = 243;
        public const short MeldungTuerOffen = 244;
        public const short MeldungGeraetefilter = 245;
        public const short MeldungVorgelagerterFilter = 246;
        public const short MeldungNiedertarif = 247;
        public const short MeldungVersorgungsspannung = 248;
        public const short MeldungPressostat = 250;
        public const short MeldungEVUSperreExtern = 251;
        public const short MeldungHeizmodulTestbetrieb = 252;
        public const short MeldungNotbetrieb = 253;
        public const short MeldungZuluftZuKalt = 254;

        // 3xx
        public const short Raum0TemperaturIst = 359;
        public const short Raum0TemperaturSoll = 399;

        // 4xx
        public const short Raum0ZusatzheizungFreigabe = 439;
        public const short Raum0ZusatzheizungStatus = 459;

        // 8xx
        public const short BetriebsstundenEWT = 813;
    }
}
