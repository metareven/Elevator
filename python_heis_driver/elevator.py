from driver import Driver
from IO import io
from channels import *
from screamer import Screamer
from multiprocessing import *
import time

class Elevator:
    DIRECTION_UP = 1
    DIRECTION_DOWN = -1
    DIRECTION_STAND = 0
    LEAVE_DOORS_OPEN = 2

    def __init__(self):
        self.driver = Driver()
        self.previous_floor = 1
        self.direction = self.DIRECTION_UP
        self.queue = [] #A Queue of orders
        self.task = [] # The current order that is being taken care of
        self.motor_speed = 1000
        self.elevator = None


    def go_to_floor(self, floor,lock):
		"""does what its name implies"""
		current_floor =self.driver.getCurrentFloor()
		if not current_floor:
			current_floor = self.previous_floor
		if current_floor < floor:
			self.direction = self.DIRECTION_UP
			self.driver.move(OUTPUT.MOTOR_UP,self.motor_speed)
		elif current_floor == floor:
			self.driver.stop()
			self.pop_task(lock)
		elif current_floor > floor:
			self.driver.move(OUTPUT.MOTOR_DOWN,self.motor_speed)



    def pop_task(self,lock):
         """removes a task from the list of tasks and preforms cleanup"""
         lock.acquire()
         floor = self.task.pop()
         lock.release()
         light = self.driver.getAccordingLight(INPUT.IN_BUTTONS,floor)
         self.driver.setChannel(light,0)
         self.open_doors()

    def open_doors(self):
         """simulates opening the doors of the elevator and waiting"""
         start = time.clock()
         while time.clock < self.LEAVE_DOORS_OPEN + start:
            self.driver.stop()

    def add_job(self,floor,direction,lock):
         """adds a job to the queue or task"""
         if task:
            #check whether this could be added as a subtask
            if self.direction == self.DIRECTION_UP == direction and self.previous_floor < floor <=self.task[len(self.task)-1][0]:
                self.add_subtask(floor,direction)
            elif self.direction == self.DIRECTION_DOWN == direction and self.previous_floor > floor >=self.task[len(self.task)-1][0]:
                self.add_subtask(floor,direction,lock)
            else:
                lock.acquire()
                self.queue.append((floor,direction))
                lock.release()
         else:
            lock.acquire()
            task.append((floor,direction))
            lock.release()

    def add_subtask(self,floor,direction,lock):
         """adds a subtask to the task in correct order"""
         lock.acquire()
         for i,sub in enumerate(self.task):
            if direction == self.DIRECTION_DOWN:
                if sub >= self.task[i]:
                    self.task.insert(sub,i)
            else:
                if sub <= self.task[i]:
                    self.task.insert(sub,i)
         lock.release()













    def read_inputs(self,lock):
        """reads inputs and processes them"""
        for sig in INPUT.BUTTONS:
			if self.driver.readChannel(sig):
				(floor,type) = self.driver.channelToFloor(sig)
				light = self.driver.getAccordingLight(type, floor)
				self.driver.setChannel(light, 1)
				if type == INPUT.IN_BUTTONS:
                                        self.add_subtask(floor,self.direction,lock)

				elif type == INPUT.DOWN_BUTTONS:
                                    job = (floor,self.DIRECTION_DOWN)
                                    if self.check_job(job):
                                        self.add_job(floor,self.DIRECTION_DOWN,lock)
                                    else:
                                        Process(target=self.elevator.send_job,args=(self.elevator,job)).start()
				elif type == INPUT.UP_BUTTONS:
                                    job = (floor,self.DIRECTION_UP)
                                    if self.check_job(job):
                                        self.add_job(floor,self.DIRECTION_UP,lock)
                                    else:
                                        Process(target=self.elevator.send_job,args=(self.elevator,job)).start()
        if self.driver.readChannel(INPUT.OBSTRUCTION):
            self.driver.stop()
        floor = self.driver.getCurrentFloor()
        if floor:
            self.driver.setFloorIndicator(floor)
            self.previous_floor = floor


    def check_job(self,job):
        """checks whether or not this elevator wants the given job"""
        (floor,direction) = job
        if not task:
            return True
        elif self.direction == self.DIRECTION_UP == direction and self.previous_floor < floor <=self.task[len(self.task)-1][0]:
            return True
        elif self.direction == self.DIRECTION_DOWN == direction and self.previous_floor > floor >=self.task[len(self.task)-1][0]:
            return True
        else:
            return False


	def reset_lights(self):
		for l in OUTPUT.LIGHTS:
			self.driver.setChannel(l, 0)

	def pick_from_queue(self):
		"""picks the next suitable job from the queue"""
        counter = 0
        while True:
            for i in len(self.queue):
                if abs(self.queue[i][0] - counter) <= counter:
                    self.task.append(self.queue[i])


	def start(self,handler):
		"""starts the elevator"""
        self.handler = handler
        lock = Lock()
        input_reader = Process(target=read_inputs,args=(self,lock))
        input_reader.start()
        while True:
            if self.task:
                self.go_to_floor(self.task[0][0],lock)
            elif self.queue:
                lock.acquire()
                self.pick_from_queue()
                lock.release()
        input_reader.terminate()



def main():
	e = Elevator()
	e.reset_lights()
	while not e.read_inputs():
		pass

if __name__ == "__main__":
	main()
