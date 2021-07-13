from solid import *
from solid.utils import *
import os
import toml


# create a filament winder
# this includes a motor that has a wedge to fit a standard 3D printing
# filament spool on. the motor is a NEMA17 stepper motor and the wedge fits
# directly on the shaft. the motor is attached to a stand that can rest on
# a table. the filament spool rests on a curved surface with the stand that
# acts as a bushing to take the load off the motor.
# a small mounting bracket is used to hold a usb laptop camera to measure
# the diameter of the filament in front of the filament spool
#  and control the motor. the rest of the electronics are not
# part of this design.

# begin scad code
def filament_winder(spool_diameter, screw_diameter, motor_screw_x, motor_screw_y,
                    spool_base_width, spool_base_height,
                    camera_mount_height, camera_mount_width,
                    camera_mount_x, camera_mount_y,
                    camera_filament_offset, filament_max_diameter,
                    motor_length, motor_width, motor_height,
                    motor_shaft_diameter, spool_shaft_diameter,
                    wall_thickness):
    '''
    returns a solidpython OpenSCAD object representing a filament winder
    PARAMETERS:
        spool_diameter: the diameter of the spool
    '''
    # create a square of four cylinders of screw_diameter placed at each corner using motor_screw parameters
    screw = cylinder(d=screw_diameter, h=wall_thickness, center=True)
    top_right_screw = translate([motor_screw_x, motor_screw_y, 0])(screw)
    bottom_right_screw = translate([-motor_screw_x, motor_screw_y, 0])(screw)
    bottom_left_screw = translate([-motor_screw_x, -motor_screw_y, 0])(screw)
    top_left_screw = translate([motor_screw_x, -motor_screw_y, 0])(screw)

    # SPOOL MOUNTS
    # create the mounting bracket which is two perpendicular squares that hold the motor
    lower_bracket = cube(
        [motor_width, motor_length, wall_thickness], center=True)
    upper_bracket = cube(
        [motor_width, motor_length, wall_thickness], center=True)
    # rotate the upper to sit at the edge of the lower
    upper_bracket = rotate([90, 0, 0])(upper_bracket)
    # translate the upper to the correct position
    upper_bracket = translate(
        [0, -motor_length/2 + wall_thickness/2, motor_width/2])(upper_bracket)

    # remove the screws from the bracket lower bracket
    lower_bracket = lower_bracket - hole()(top_right_screw) - hole()(
        bottom_right_screw) - hole()(bottom_left_screw) - hole()(top_left_screw)

    motor_bracket = upper_bracket + lower_bracket

    # create the spool base as a large rectangular prism
    spool_base = cube([spool_base_width, spool_base_height,
                      wall_thickness], center=True)
    spool_base = translate([0, motor_length/2, 0])(spool_base)
    # create a spool which will be subtracted from the spool base
    spool = cylinder(d=spool_diameter, h=spool_base_height, center=True)
    # rotate the spool to the correct position
    spool = rotate([90, 0, 0])(spool)
    # translate the spool to the correct position
    spool = translate([0, motor_length/2, spool_diameter/2])(spool)

    # subtract the spool from the spool base to create the spool bushing to take the load off the motor
    spool_base = spool_base - spool

    # create a rectangular prism that will go from the outside of the spool base
    # to the motor
    spool_base_motor = cube([motor_width, motor_length, spool_diameter/2], center=True)
    spool_base_motor = translate(
        [0, 0, spool_diameter/4 - wall_thickness/2])(spool_base_motor)
    # move the spool base motor to the left most part of the spool base
    spool_base_motor = translate([0, -spool_base_height/2, 0])(spool_base_motor)

    spool_base_motor_right = spool_base_motor
    lower_bracket = cube(
        [motor_width, motor_length, wall_thickness], center=True)
    upper_bracket = cube(
        [motor_width, motor_length, wall_thickness], center=True)
    # rotate the upper to sit at the edge of the lower
    upper_bracket = rotate([90, 0, 0])(upper_bracket)
    # translate the upper to the correct position
    upper_bracket = translate(
        [0, -motor_length/2 + wall_thickness/2, motor_width/2])(upper_bracket)
    bracket = upper_bracket + lower_bracket
    # add the bracket to the top of the spool base motor right
    bracket = up(spool_diameter/2)(bracket)
    # move the bracket to the center of the spool base motor right
    bracket = translate([0, -spool_base_height/2, 0])(bracket)

    # rotate the motor bracket to 90 degrees to fit the spool base
    motor_bracket = rotate([90, 0, 0])(motor_bracket)
    # move the motor bracket to the correct position atop the spool base
    motor_bracket = translate(
        [0, -spool_base_height/2 + wall_thickness/2, 0])(motor_bracket)
    motor_bracket = translate([0, 0, spool_diameter/2])(motor_bracket)
    motor_bracket = up(motor_length/2 - wall_thickness/2)(motor_bracket)
    # move forward in the y axis by the motor width divided by two
    motor_bracket = translate([0, motor_width/2 - wall_thickness, 0])(motor_bracket)

    # subtract a cylinder from the brackets to create the motor shaft
    motor_shaft = cylinder(d=motor_shaft_diameter, h=2*spool_base_height, center=True)
    # rotate the motor shaft to the correct position
    motor_shaft = rotate([90, 0, 0])(motor_shaft)
    # move the motor shaft to the correct position with the center of both brackets
    motor_shaft = translate([0, 0, spool_diameter/2 + motor_length/2])(motor_shaft)

    # CAMERA MOUNT
    # create the camera mount to hold the camera
    # the camera will be zip tied to the mount for now so it can just be a cube
    camera_mount = cube([camera_mount_width, camera_mount_height,
                        wall_thickness], center=True)

    # create a cube to hold the camera mount to the motor's spool base as a L shaped connection of two
    # cubes
    # first create the x length of the support
    camera_mount_support_x = cube(
        [camera_mount_x, wall_thickness, wall_thickness], center=True)
    # create the y length of the support
    camera_mount_support_y = cube(
        [wall_thickness, camera_mount_y, wall_thickness], center=True)

    # add two loops that will act as filament guides over the camera mount support
    filament_loop = cylinder(d=wall_thickness, h=camera_mount_width/3, center=True)
    # cut a hole out of the loop to make it a filament guide
    filament_loop = filament_loop - hole()(cylinder(d=filament_max_diameter,
                                                    h=camera_mount_width/3, center=True))

    # place two filament_loops at the front and back of the camera_mount
    camera_mount = camera_mount + translate([camera_mount_width/3, 0, camera_filament_offset])(
        rotate([0, 90, 0])(filament_loop))
    camera_mount = camera_mount + translate([-camera_mount_width/3, 0, camera_filament_offset])(
        rotate([0, 90, 0])(filament_loop))
    # connect the camera mount with the loops using cylinders translated to the outside of the camera mount in the y axis using  camera_mount_height
    # the cylinders will need to have height camera_filament_offset and diameter wall_thickness
    camera_mount = camera_mount + translate([camera_mount_width/2 - wall_thickness/2, 0, camera_filament_offset/2])(
        cylinder(d=wall_thickness, h=camera_filament_offset, center=True))
    camera_mount = camera_mount + translate([-camera_mount_width/2 + wall_thickness/2, 0, camera_filament_offset/2])(
        cylinder(d=wall_thickness, h=camera_filament_offset, center=True))

    # move the y to the end of the x
    camera_mount_support_y = translate([camera_mount_x/2, 0, 0])(camera_mount_support_y)
    # move the y forward
    camera_mount_support_y = translate(
        [0, camera_mount_y/2 - wall_thickness/2, 0])(camera_mount_support_y)
    # offset the y length by the x length
    camera_mount_support = camera_mount_support_x + camera_mount_support_y
    # move the support to the corner of the motors spool base
    camera_mount_support = translate(
        [2*motor_width, 0, 0])(camera_mount_support)
    # move the support to the correct position in the x axis
    camera_mount_support = translate(
        [0, -spool_base_height/2 + motor_length/2 - wall_thickness/2, 0])(camera_mount_support)

    # move the camera mount into position in front of the camera_mount_support
    camera_mount = translate([camera_mount_x, camera_mount_y, 0])(camera_mount)
    camera_mount = translate(
        [camera_mount_width/2, camera_mount_height/2, 0])(camera_mount)
    # move the camera mount by half its respective dimensions
    camera_mount = translate(
        [0, -spool_base_height/2 + motor_length/2 - wall_thickness, 0])(camera_mount)

    filament_winder = spool_base + spool_base_motor + motor_bracket + \
        camera_mount_support + camera_mount
    # remove the shafts
    filament_winder = filament_winder - hole()(motor_shaft)
    return filament_winder


def render_object(render_object, filename):
    '''
    creates a .stl and .scad solution for the given solidpython OpenSCAD object
    PARAMETERS:
        render_object: the OpenSCAD object
        filename: a string for the file to be saved
    '''
    scad_render_to_file(render_object, filename +
                        ".scad", file_header='$fn=200;')
    # render with OpenSCAD
    print("Openscad is now rendering the solution..")
    os.system("/home/bada/Desktop/code/openscad/openscad -o " +
              filename + ".stl " + filename + ".scad")


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    filament_winder(**config)
    # carbon_filter = Carbon_Filter(**config)
    # render_object(carbon_filter, "filter")
    filament_winder = filament_winder(**config)
    render_object(filament_winder, "filament_winder")
