from setuptools import find_packages, setup

package_name = 'iha_controllers'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='inci',
    maintainer_email='inci@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'camera_controller = iha_controllers.camera_controller:main',
            'imu_controller = iha_controllers.imu_controller:main',
            'gps_controller = iha_controllers.gps_controller:main',
            'baro_controller = iha_controllers.baro_controller:main',
            'lidar_controller = iha_controllers.lidar_controller:main',
            'servo_motor_controller = iha_controllers.servo_motor_controller:main',
        ],
    },
)
