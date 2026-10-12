# Register the ROS Python package, launch file and six console entry points.
import os
from glob import glob
from setuptools import setup

package_name = 'avone'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vehicle_publisher = avone.vehicle_publisher:main',
            'cruise_control = avone.cruise_control:main',
            'lane_detector = avone.lane_detector:main',
            'motor_control = avone.motor_control:main',
            'speed_publisher = avone.speed_publisher:main',
            'image_publisher = avone.image_publisher:main',
        ],
    },
)
