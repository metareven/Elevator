from driver import Driver
from IO import io
from channels import *
from screamer import Screamer
from multiprocessing import *
import time

class Elevator:
	DIRECTION_UP = 0
	DIRECTION_DOWN = 1
	DIRECTION_STAND = -1
	LEAVE_DOORS_OPEN = 2

	def __init__(self):
		self.driver = Driver()
		self.previous_floor = 1
		self.direction = self.DIRECTION_UP
		self.queue = []


	def go_to_floor(self, floor):
		current_floor =self.driver.getCurrentFloor()
		if not current_floor:
			current_floor = self.previous_floor
		if current_floor < floor:
			self.direction = self.DIRECTION_UP
		elif current_floor == floor:
			self.driver.stop()


	def pop_queue(self):
         floor = self.queue.pop()
         light = self.driver.getAccordingLight(INPUT.IN_BUTTONS,floor)
         self.driver.setChannel(light,0)
         self.open_doors()

	def open_doors(self):
         """simulates opening the doors of the elevator and waiting"""
         time.sleep(self.LEAVE_DOORS_OPEN)

	def add_to_queue(self,floor,direction):
         """adds a job to the queue"""
         calc_dir = self.direction
         for i, job in enumerate(self.queue):
            if calc_dir == direction and floor < job :
                self.queue.insert((floor,direction),i)
            elif i < len(self.queue)-1:
                (qf,qd) = job
                (qf2,qd2) = self.queue[i+1]
                calc_dir = self.DIRECTION_DOWN if qf - qf2 > 0 else self.DIRECTION_DOWN
            #TODO: A LOT I GUESS



	def read_inputs(self):
		for sig in INPUT.BUTTONS:
			if self.driver.readChannel(sig):
				(floor,type) = self.driver.channelToFloor(sig)
				light = self.driver.getAccordingLight(type, floor)
				self.driver.setChannel(light, 1) # Skrur p lyset til knappen som er trykket p
				if type == INPUT.IN_BUTTONS:
					pass
				elif type == INPUT.DOWN_BUTTONS:
					pass
					#skru p lys i ned-knappen p etasje floor
					# og legg til floor i ken til heisen samt dens retning (en tuppel)
				elif type == INPUT.UP_BUTTONS:
					pass
					#skru p lys i opp-knappen p etasje floor
					# og legg til floor i ken til heisen samt dens retning (en tuppel)
		# sjekk obstruction

	def reset_lights(self):
		for l in OUTPUT.LIGHTS:
			self.driver.setChannel(l, 0)

def main():
	e = Elevator()
	e.reset_lights()
	while not e.read_inputs():
		pass

if __name__ == "__main__":
	main()
