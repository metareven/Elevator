import driver
import time
import channels

def main():
	d = driver.Driver()
	#d.move(channels.OUTPUT.MOTOR_UP, 1000)
	#time.sleep(2)
	d.stop()

if __name__ == '__main__':
	main()
