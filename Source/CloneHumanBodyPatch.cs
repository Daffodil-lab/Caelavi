using System.Xml;
using Verse;

namespace Caelavi;

/// <summary>
/// Derive the Caelavi anatomy from the installed game's Human body at XML load
/// time. This keeps the complete vanilla anatomy supplied by the current game
/// version without shipping a copy of its BodyDef.
/// </summary>
public sealed class CloneHumanBodyPatch : PatchOperation
{
    protected override bool ApplyWorker(XmlDocument xml)
    {
        XmlNode? human = xml.SelectSingleNode("/Defs/BodyDef[defName='Human']");
        if (human?.ParentNode == null)
        {
            Log.Error("[Caelavi] Cannot create CA_HumanWinged: Core Human BodyDef is missing from the unified XML.");
            return false;
        }

        if (xml.SelectSingleNode("/Defs/BodyDef[defName='CA_HumanWinged']") != null)
        {
            Log.Error("[Caelavi] Cannot create CA_HumanWinged: that BodyDef already exists.");
            return false;
        }

        XmlElement body = (XmlElement)human.CloneNode(deep: true);
        XmlNode? defName = body.SelectSingleNode("defName");
        XmlNode? parts = body.SelectSingleNode("corePart/parts");
        if (defName == null || parts == null)
        {
            Log.Error("[Caelavi] Cannot create CA_HumanWinged: Core Human BodyDef has no defName or corePart/parts.");
            return false;
        }

        defName.InnerText = "CA_HumanWinged";
        XmlNode? label = body.SelectSingleNode("label");
        if (label != null)
        {
            label.InnerText = "Caelavi";
        }

        // 0.06 coverage per wing is an alpha tuning value. Both wings together
        // leave the vanilla Human torso's immediate coverage below 1.0.
        parts.AppendChild(NewWing(xml, "left wing", mirrored: true));
        parts.AppendChild(NewWing(xml, "right wing", mirrored: false));
        human.ParentNode.AppendChild(body);
        return true;
    }

    private static XmlElement NewWing(XmlDocument xml, string side, bool mirrored)
    {
        XmlElement wing = xml.CreateElement("li");
        AddText(xml, wing, "def", "CA_Wing");
        AddText(xml, wing, "customLabel", side);
        AddText(xml, wing, "coverage", "0.06");
        AddText(xml, wing, "height", "Middle");
        AddText(xml, wing, "depth", "Outside");
        if (mirrored)
        {
            AddText(xml, wing, "flipGraphic", "true");
        }

        XmlElement groups = xml.CreateElement("groups");
        AddText(xml, groups, "li", "CA_Wings");
        wing.AppendChild(groups);
        return wing;
    }

    private static void AddText(XmlDocument xml, XmlElement parent, string name, string value)
    {
        XmlElement child = xml.CreateElement(name);
        child.InnerText = value;
        parent.AppendChild(child);
    }
}
