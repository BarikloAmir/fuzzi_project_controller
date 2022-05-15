# -*- coding: utf-8 -*-

# python imports
import random
from math import degrees
import random
# pyfuzzy imports
from fuzzy.storage.fcl.Reader import Reader
import rules

def calculate_fuzzi_value(location_list, input_x):
    x1 = location_list[0]
    x2 = location_list[1]
    x3 = location_list[2]

    if input_x == x2:
        return 1
    if input_x <= x1 or input_x >= x3:
        return 0
    if input_x<x2:
        return abs(input_x-x1)/abs(x2-x1)
    if input_x>x2:
        return abs(x3-input_x)/abs(x3-x2)


def calculate_point_value(x, location_dictionary_force,fuzzi_output_value_dict):
    value = 0
    for key in location_dictionary_force:
        x_location1 = location_dictionary_force.get(key)[0]
        x_location2 = location_dictionary_force.get(key)[2]
        if x_location1 <= x <= x_location2:
            value_temp = calculate_fuzzi_value(location_dictionary_force.get(key),x)
            #print("key",key,"  ",value_temp,"   ",fuzzi_output_value_dict.get(key))
            if value_temp>fuzzi_output_value_dict.get(key):
                value_temp = fuzzi_output_value_dict.get(key)
            if value_temp>value:
                value = value_temp

    return value


def calculate_crime_point(point_values_dict,delta):
    sum_up = 0
    sum_down = 0
    for x in point_values_dict.keys():
        fx = point_values_dict.get(x)
        sum_up += x*fx*delta
        sum_down += fx*delta

    try:
        return sum_up/sum_down
    except:
        print("===>error===>",point_values_dict)
        return sum_up/sum_down


class FuzzyController:
    # pa
    location_dictionary_pa = {

        "up_more_right": [0,30,60],

        "up_right" : [30,60,90],

        "up" : [60,90,120],

        "up_left" : [90,120,150],

        "up_more_left" : [120,150,180],

        "down_more_left" : [180,210,240],

        "down_left" : [210,240,270],

        "down" : [240,270,300],

        "down_right" : [270,300,330],

        "down_more_right" : [300,330,360]}

    # pv
    location_dictionary_pv={
        "cw_fast" : [-4040000,-200,-100],

        "cw_slow" : [-200,-100,0],

        "stop_pv" : [-100,0,100],

        "ccw_slow" :[0,100,200],

        "ccw_fast" : [100,200,404000]}

    # cp
    location_dictionary_cp = {
        "left_far" : [-4040000,-10,-5],

        "left_near" : [-10,-2.5,0],

        "stop_cp" : [-2.5,0,2.5],

        "right_near" : [0,2.5,10],

        "right_far" : [5,10,+404000]}

    # cv
    location_dictionary_cv = {
        "left_fast" : [-404000,-5,-2.5],

        "left_slow" : [-5,-1,0],

        "stop_cv" : [-1,0,1],

        "right_slow" : [0,1,5],

        "right_fast" : [2.5,5,404000]}

    # force
    location_dictionary_force = {
        "left_fast" : [-100,-80,-60],

        "left_slow" : [-80,-60,0],

        "stop" : [-60,0,60],

        "right_slow" : [0,60,80],

        "right_fast" : [60,80,100]}

    def __init__(self, fcl_path):
        self.system = Reader().load_from_file(fcl_path)


    def _make_input(self, world):
        return dict(
            cp = world.x,
            cv = world.v,
            pa = degrees(world.theta),
            pv = degrees(world.omega)
        )


    def _make_output(self):
        return dict(
            force = 0.
        )

    def fuzzification(self, input_value_dict):
        cp = input_value_dict.get('cp')
        cv = input_value_dict.get('cv')
        pa = input_value_dict.get('pa')
        pv = input_value_dict.get('pv')
        #print(cp,cv,pv,pa)
        if pa<0:
            pa = 360 - abs(pa)

        fuzzi_value_dict = {}

        for key in self.location_dictionary_pa:
            fuzzi_value_dict[key] = calculate_fuzzi_value(self.location_dictionary_pa[key],pa)

        for key in self.location_dictionary_pv:
            fuzzi_value_dict[key] = calculate_fuzzi_value(self.location_dictionary_pv[key],pv)

        for key in self.location_dictionary_cp:
            fuzzi_value_dict[key] = calculate_fuzzi_value(self.location_dictionary_cp[key], cp)

        for key in self.location_dictionary_cv:
            fuzzi_value_dict[key] = calculate_fuzzi_value(self.location_dictionary_cv[key],cv)
        #print(fuzzi_value_dict)
        return fuzzi_value_dict

    def inference(self, fuzzi_value_dict):
        #print(fuzzi_value_dict,"\n\n\n")
        fuzzi_output_value_dict = {}
        for rule in rules.rules_list:
            item1 = fuzzi_value_dict[rule[0]]
            #print("item1",item1,rule[0])
            item2 = fuzzi_value_dict[rule[1]]
            #print("item2",item2,rule[1])
            output_item = rule[2]
            #print("outputitem",output_item)
            if fuzzi_output_value_dict.get(output_item) is None:
                fuzzi_output_value_dict[output_item] = min(item1,item2)

            else:
                if fuzzi_output_value_dict[output_item] < min(item1,item2):
                    fuzzi_output_value_dict[output_item] = min(item1, item2)

        return fuzzi_output_value_dict


    def defuzzification(self,fuzzi_output_value_dict):
        delta = .1
        x = -100
        point_values_dict = {}
        while x<=100:
            fx=calculate_point_value(x,self.location_dictionary_force,fuzzi_output_value_dict)
            point_values_dict[x]=fx
            x+=delta


        return calculate_crime_point(point_values_dict,delta)





    def decide(self, world):
        output = self._make_output()

        fuzzi_value_dict = self.fuzzification(self._make_input(world))
        fuzzi_output_value_dict = self.inference(fuzzi_value_dict)
        force = self.defuzzification(fuzzi_output_value_dict)

        output['force'] = force

        return output['force']
    decide.counter =0