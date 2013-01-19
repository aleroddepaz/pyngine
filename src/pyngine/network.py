from pyngine import * #@UnusedWildImport
import socket
from threading import Thread


class GameServer(Game):
    
    players = []
    input = {}
    
    def start_server(self, port):
        self.address = ('localhost', port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)
        self.socket.listen(99)
        self.thread = Thread(target=self.handle_connections)
        self.thread.start()

    def handle_connections(self):
        while not Input.quitflag:
            conn, addr = self.socket.accept()
            input_data = json.loads(conn.recv())
            GameServer.input[addr] = input_data

    def gameloop(self, fps=60, port):
        self.start_server(port)
        step = 1. / fps
        clock = pygame.time.Clock()
        while not Input.quitflag:
            self.scene.update()
            PhysicsEngine.step(step)
            delta = clock.tick(fps)
            Game.delta = delta / 1000.

class GameClient(Game):
    
    def gameloop(self, player, fps=60, host, port):
        Input.connect_server(host, port, player)
        clock = pygame.time.Clock()
        while not Input.quitflag:
            data = Input.update_client()
            self._renderloop(data)
            delta = clock.tick(fps)
            Game.delta = delta / 1000.
    
    def _renderloop(self, data):
        render_info = json.loads(data)
        print render_info
