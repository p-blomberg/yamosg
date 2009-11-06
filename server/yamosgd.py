# the actual game server
import server

if __name__ == "__main__":
	s=server.Server("0.0.0.0", 1234, 5)
	s.main()
