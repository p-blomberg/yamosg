import connection
import game
import object
import planet
import player
import server
import ship
import sockets
import staion

if __name__ == "__main__":
	s=Server("0.0.0.0", 1234, 5)
	s.main()
