        if 'left' in hands:
            d = self.draw_line("left", 4, 8)
            self.update_volume(d)
        if 'right' in hands:
            if self.draw_angle("right", 4, 8) and time.time()-self.last_angle > self.angle_delay:
                self.keyboard.next_song()
                self.last_angle = time.time()
            self.draw_touch("right", 8)