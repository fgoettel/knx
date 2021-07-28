// Author: Fabian Göttel
// Copyright (c) Fabian  Göttel
// See LICENSE in the project root for license information.

namespace Fabian_goettel_gmail_com.Logic.Wgt
{
    using System.Collections.Generic;

    /// <summary>
    /// Exchange WGT address.
    /// </summary>
    public static class WgtEnums
    {
        public static readonly Dictionary<string, short> Betriebsarten
            = new Dictionary<string, short>
                {
                    { "Aus", 0},
                    { "Handbetrieb", 1},
                    { "Winterbetrieb", 2},
                    { "Sommerbetrieb", 3},
                    { "Sommer Abluft", 4}
                };

        public static readonly Dictionary<string, short> Bypass
            = new Dictionary<string, short>
                {
                    { "Bypass geschlossen", 0},
                    { "Bypass offen (Kühlen)", 1},
                    { "Bypass offen (Heizen)", 2}
                };

        public static readonly Dictionary<string, short> Fehlermeldung
            = new Dictionary<string, short>
                {
                    {"Kein Fehler", 0},
                    {"Drehzahl Zuluft fehlt", 257},
                    {"Drehzahl Abluft fehlt", 258},
                    {"Ventilator Zuluft Mindestdrehzahl nicht erreicht", 259},
                    {"Ventilator Abluft Mindestdrehzahl nicht erreicht", 260},
                    {"Ventilator Zuluft max. Drehzahl überschritten", 261},
                    {"Ventilator Abluft max. Drehzahl überschritten", 262},
                    {"Kommunikationsfehler zur BDE", 513},
                    {"Kommunikationsfehler Nebenbedieneinheit", 514},
                    {"Kommunikationsfehler Heizmodul", 515},
                    {"Kommunikationsfehler Sensor", 516},
                    {"Kommunikationsfehler Sensor-Adapter", 517},
                    {"Kommunikation Empfänger", 518},
                    {"Fehler Sensorelement T1-nach-Ewt", 770},
                    {"Fehler Sensorelement T2-nachVhr", 771},
                    {"Fehler Sensorelement T3-vorNhr", 772},
                    {"Fehler Sensorelement T4-nachNhr", 773},
                    {"Fehler Sensorelement T5-Abluft", 774},
                    {"Fehler Sensorelement T6-imWT", 775},
                    {"Fehler Sensorelement T7-Verdampfer", 776},
                    {"Fehler Sensorelement T8-Kondensator", 777},
                    {"Fehler Sensorelement T10-Außentemperatur", 779},
                    {"Fehler Parameterspeicher", 1025},
                    {"Fehler System-Bus", 1026},
                    {"Wärmepumpe Hochdruck", 1281},
                    {"Wärmepumpe Niederdruck", 1282},
                    {"Maximale Abtauzeit überschritten", 1283},
                    {"Wärmepumpe Niederdruck im Kühlbetrieb", 1284}
                };

        public static readonly Dictionary<string, short> Luftstufe
            = new Dictionary<string, short>
                {
                    { "Aus", 0},
                    { "Stufe 1", 1},
                    { "Stufe 2", 2},
                    { "Stufe 3", 3},
                    { "Stufe 4", 4},
                    { "Automatik", 5},
                    { "Linearbetrieb", 6}
                };

        public static readonly Dictionary<string, short> WaermepumpeStatus
            = new Dictionary<string, short>
                {
                    { "Aus", 0},
                    { "WP Heizen", 5},
                    { "WP Kühlen", 49}
                };

        public static readonly Dictionary<string, short> Meldungen
            = new Dictionary<string, short>
                {
                    {"Druckwächter Aktiv", Addr.MeldungDruckwächter},
                    {"EVU Sperre Aktiv", Addr.MeldungEVUSperre},
                    {"Tür offen", Addr.MeldungTuerOffen},
                    {"Gerätefilter verschmutzt", Addr.MeldungGeraetefilter},
                    {"Vorgelagerter Filter verschmutzt", Addr.MeldungVorgelagerterFilter},
                    {"Niedertarif abgeschaltet", Addr.MeldungNiedertarif},
                    {"Versorgungsspannung abgeschaltet", Addr.MeldungVersorgungsspannung},
                    {"Pressostat ausgelöst", Addr.MeldungPressostat},
                    {"EVU Sperre extern Aktiv", Addr.MeldungEVUSperreExtern},
                    {"Heizmodul Testbetrieb aktiv", Addr.MeldungHeizmodulTestbetrieb},
                    {"Notbetrieb aktiv", Addr.MeldungNotbetrieb},
                    {"Zuluft zu kalt", Addr.MeldungZuluftZuKalt}
                };

    }
}
