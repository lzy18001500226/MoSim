from glob import glob
from setuptools import setup


package_name = "mosim_scene_replay"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="MoSim",
    maintainer_email="devnull@example.com",
    description="MoSim UE scene ROS2 replay launch package for RViz2 review.",
    license="Proprietary",
)
