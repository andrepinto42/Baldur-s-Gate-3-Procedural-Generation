import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

xml_text = """<children>
								<node id="tile">
									<attribute id="UUID" type="FixedString" value="f826c52e-f1e1-4691-9c86-c6afb8506378" />
									<attribute id="tile" type="guid" value="88c8ec1e-dd7b-469c-aefa-af3277e6f6c0" />
									<attribute id="Translate" type="fvec3" value="-8.854665 0 66.88342" />
									<attribute id="QRotate" type="fvec4" value="0 -0.70710677 0 0.70710677" />
									<attribute id="Scale" type="float" value="1" />
									<attribute id="ScaleZ" type="float" value="1" />
									<attribute id="Climbable" type="bool" value="False" />
									<attribute id="WalkOn" type="bool" value="False" />
									<attribute id="Stretchable" type="bool" value="False" />
									<attribute id="Flip" type="bool" value="False" />
									<attribute id="ShootThrough" type="bool" value="False" />
									<attribute id="ShootThroughType" type="int8" value="6" />
									<attribute id="WalkThrough" type="bool" value="False" />
									<attribute id="ClickThrough" type="bool" value="False" />
									<attribute id="CanSeeThrough" type="bool" value="False" />
								</node>
								<node id="tile">
									<attribute id="UUID" type="FixedString" value="eef98063-376b-4335-b1db-729ecab18759" />
									<attribute id="tile" type="guid" value="21fb351f-b774-461d-a2d2-bd974f4e693f" />
									<attribute id="Translate" type="fvec3" value="-8.854665 0 66.88342" />
									<attribute id="QRotate" type="fvec4" value="0 0.7071067 0 0.7071068" />
									<attribute id="Scale" type="float" value="1" />
									<attribute id="ScaleZ" type="float" value="0.9894829" />
									<attribute id="Climbable" type="bool" value="False" />
									<attribute id="WalkOn" type="bool" value="False" />
									<attribute id="Stretchable" type="bool" value="True" />
									<attribute id="Flip" type="bool" value="False" />
									<attribute id="ShootThrough" type="bool" value="False" />
									<attribute id="ShootThroughType" type="int8" value="6" />
									<attribute id="WalkThrough" type="bool" value="False" />
									<attribute id="ClickThrough" type="bool" value="False" />
									<attribute id="CanSeeThrough" type="bool" value="False" />
								</node>
								<node id="tile">
									<attribute id="UUID" type="FixedString" value="f8a56432-5923-4632-a4e1-e42008e1be9e" />
									<attribute id="tile" type="guid" value="21fb351f-b774-461d-a2d2-bd974f4e693f" />
									<attribute id="Translate" type="fvec3" value="-8.854665 0 62.92549" />
									<attribute id="QRotate" type="fvec4" value="0 0.7071067 0 0.7071068" />
									<attribute id="Scale" type="float" value="1" />
									<attribute id="ScaleZ" type="float" value="0.9894829" />
									<attribute id="Climbable" type="bool" value="False" />
									<attribute id="WalkOn" type="bool" value="False" />
									<attribute id="Stretchable" type="bool" value="True" />
									<attribute id="Flip" type="bool" value="False" />
									<attribute id="ShootThrough" type="bool" value="False" />
									<attribute id="ShootThroughType" type="int8" value="6" />
									<attribute id="WalkThrough" type="bool" value="False" />
									<attribute id="ClickThrough" type="bool" value="False" />
									<attribute id="CanSeeThrough" type="bool" value="False" />
								</node>
								<node id="tile">
									<attribute id="UUID" type="FixedString" value="c54f6e89-8af2-41a5-b266-cefda2e47161" />
									<attribute id="tile" type="guid" value="21fb351f-b774-461d-a2d2-bd974f4e693f" />
									<attribute id="Translate" type="fvec3" value="-7.854664 0 54.99911" />
									<attribute id="QRotate" type="fvec4" value="0 0 0 1" />
									<attribute id="Scale" type="float" value="1" />
									<attribute id="ScaleZ" type="float" value="1.0220633" />
									<attribute id="Climbable" type="bool" value="False" />
									<attribute id="WalkOn" type="bool" value="False" />
									<attribute id="Stretchable" type="bool" value="True" />
									<attribute id="Flip" type="bool" value="False" />
									<attribute id="ShootThrough" type="bool" value="False" />
									<attribute id="ShootThroughType" type="int8" value="6" />
									<attribute id="WalkThrough" type="bool" value="False" />
									<attribute id="ClickThrough" type="bool" value="False" />
									<attribute id="CanSeeThrough" type="bool" value="False" />
								</node>
								<node id="tile">
									<attribute id="UUID" type="FixedString" value="820cf3a7-ba1c-4a89-9b45-861ef6d6bcfe" />
									<attribute id="tile" type="guid" value="21fb351f-b774-461d-a2d2-bd974f4e693f" />
									<attribute id="Translate" type="fvec3" value="-3.7664108 0 54.999115" />
									<attribute id="QRotate" type="fvec4" value="0 0 0 1" />
									<attribute id="Scale" type="float" value="1" />
									<attribute id="ScaleZ" type="float" value="1.0220633" />
									<attribute id="Climbable" type="bool" value="False" />
									<attribute id="WalkOn" type="bool" value="False" />
									<attribute id="Stretchable" type="bool" value="True" />
									<attribute id="Flip" type="bool" value="False" />
									<attribute id="ShootThrough" type="bool" value="False" />
									<attribute id="ShootThroughType" type="int8" value="6" />
									<attribute id="WalkThrough" type="bool" value="False" />
									<attribute id="ClickThrough" type="bool" value="False" />
									<attribute id="CanSeeThrough" type="bool" value="False" />
								</node>
								<node id="tile">
									<attribute id="UUID" type="FixedString" value="2c924f45-9383-46c6-a1ed-d4eedba437fc" />
									<attribute id="tile" type="guid" value="88c8ec1e-dd7b-469c-aefa-af3277e6f6c0" />
									<attribute id="Translate" type="fvec3" value="0.3218422 0 54.999115" />
									<attribute id="QRotate" type="fvec4" value="0 0 0 1" />
									<attribute id="Scale" type="float" value="1" />
									<attribute id="ScaleZ" type="float" value="1" />
									<attribute id="Climbable" type="bool" value="False" />
									<attribute id="WalkOn" type="bool" value="False" />
									<attribute id="Stretchable" type="bool" value="False" />
									<attribute id="Flip" type="bool" value="False" />
									<attribute id="ShootThrough" type="bool" value="False" />
									<attribute id="ShootThroughType" type="int8" value="6" />
									<attribute id="WalkThrough" type="bool" value="False" />
									<attribute id="ClickThrough" type="bool" value="False" />
									<attribute id="CanSeeThrough" type="bool" value="False" />
								</node>
								<node id="tile">
									<attribute id="UUID" type="FixedString" value="b9cb4c6e-3568-4a03-add7-2a80cb72aba5" />
									<attribute id="tile" type="guid" value="6a21259c-ec13-4f00-8afa-f762007c64d2" />
									<attribute id="Translate" type="fvec3" value="-8.854664 0 54.99911" />
									<attribute id="QRotate" type="fvec4" value="0 0.7071067 0 0.7071068" />
									<attribute id="Scale" type="float" value="1" />
									<attribute id="ScaleZ" type="float" value="1" />
									<attribute id="Climbable" type="bool" value="False" />
									<attribute id="WalkOn" type="bool" value="False" />
									<attribute id="Stretchable" type="bool" value="False" />
									<attribute id="Flip" type="bool" value="False" />
									<attribute id="ShootThrough" type="bool" value="False" />
									<attribute id="ShootThroughType" type="int8" value="6" />
									<attribute id="WalkThrough" type="bool" value="False" />
									<attribute id="ClickThrough" type="bool" value="False" />
									<attribute id="CanSeeThrough" type="bool" value="False" />
								</node>
								<node id="tile">
									<attribute id="UUID" type="FixedString" value="6beafae8-e744-4563-ba9a-4aa54490ef37" />
									<attribute id="tile" type="guid" value="a8cbd249-34ee-4cd0-a26e-d623888c25ea" />
									<attribute id="Translate" type="fvec3" value="-8.854664 0 58.96756" />
									<attribute id="QRotate" type="fvec4" value="0 0.7071067 0 0.7071068" />
									<attribute id="Scale" type="float" value="1" />
									<attribute id="ScaleZ" type="float" value="0.9894829" />
									<attribute id="Climbable" type="bool" value="False" />
									<attribute id="WalkOn" type="bool" value="False" />
									<attribute id="Stretchable" type="bool" value="True" />
									<attribute id="Flip" type="bool" value="False" />
									<attribute id="ShootThrough" type="bool" value="False" />
									<attribute id="ShootThroughType" type="int8" value="6" />
									<attribute id="WalkThrough" type="bool" value="False" />
									<attribute id="ClickThrough" type="bool" value="False" />
									<attribute id="CanSeeThrough" type="bool" value="False" />
								</node>
								<node id="tile">
									<attribute id="UUID" type="FixedString" value="ea50f854-b8d2-4196-bde4-5479d114cead" />
									<attribute id="tile" type="guid" value="16563ec3-b859-4f12-869c-79e10428ba7a" />
									<attribute id="Translate" type="fvec3" value="-8.854664 0 56.988594" />
									<attribute id="QRotate" type="fvec4" value="0 0.7071067 0 0.7071068" />
									<attribute id="Scale" type="float" value="1" />
									<attribute id="ScaleZ" type="float" value="0.9894829" />
									<attribute id="Climbable" type="bool" value="False" />
									<attribute id="WalkOn" type="bool" value="False" />
									<attribute id="Stretchable" type="bool" value="True" />
									<attribute id="Flip" type="bool" value="False" />
									<attribute id="ShootThrough" type="bool" value="False" />
									<attribute id="ShootThroughType" type="int8" value="6" />
									<attribute id="WalkThrough" type="bool" value="False" />
									<attribute id="ClickThrough" type="bool" value="False" />
									<attribute id="CanSeeThrough" type="bool" value="False" />
								</node>
							</children>
                            """

root = ET.fromstring(xml_text)

points = []   # (x, z)
uuids = []

for node in root.findall("node"):
    translate = node.find("attribute[@id='Translate']")
    uuid_attr = node.find("attribute[@id='UUID']")

    if translate is not None:
        x, y, z = map(float, translate.attrib["value"].split())
        points.append((x, z))
        uuids.append(uuid_attr.attrib["value"] if uuid_attr is not None else None)


# sort by Z (forward direction)
points_sorted = sorted(points, key=lambda p: p[1])

xs = [p[0] for p in points_sorted]
zs = [p[1] for p in points_sorted]

plt.figure(figsize=(8, 8))
plt.plot(xs, zs, "-o", linewidth=2)
plt.scatter(xs, zs)

for i, (x, z) in enumerate(points_sorted):
    plt.text(x, z, str(i), fontsize=9)

plt.xlabel("X")
plt.ylabel("Z")
plt.title("Tile Positions (Corrected Path Order)")
plt.axis("equal")
plt.grid(True)
plt.show()