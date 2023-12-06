import pygame 
from .settings import tile_size,screen_height, screen_width
from .support import import_csv_layout, import_cut_graphics
from .tiles import Tile, StaticTile, Caixote, Moedas, Espinhos
from .enemy import Enemy
from .player import Player
from .particles import ParticleEffect
from .game_data import levels

class Level:
    def __init__(self,current_level,surface,create_overworld):
        
		# general setup
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None
        
        # overworld connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

		# player 
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

		# # level display
        # self.font = pygame.font.Font(None, 40)
        # self.text_surf = self.font.render(level_content,True,'white')
        # self.text_rect = self.text_surf.get_rect(center = (screen_width / 2, screen_height / 2))

		# dust 
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

		# estrutura
        estrutura_layout = import_csv_layout(level_data['estrutura'])
        self.estrutura_sprites = self.create_tile_group(estrutura_layout,'estrutura')

		# caixote 
        caixote_layout = import_csv_layout(level_data['caixote'])
        self.caixote_sprites = self.create_tile_group(caixote_layout,'caixote')

		# espinhos
        espinhos_layout = import_csv_layout(level_data['espinhos'])
        self.espinhos_sprites = self.create_tile_group(espinhos_layout, 'espinhos')

		# moedas 
        moedas_layout = import_csv_layout(level_data['moedas'])
        self.moedas_sprites = self.create_tile_group(moedas_layout,'moedas')

		# enemy 
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout,'enemies')

		# limite 
        limite_layout = import_csv_layout(level_data['limite'])
        self.constraint_sprites = self.create_tile_group(limite_layout,'limite')

    def create_tile_group(self,layout,type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'estrutura':
                        estrutura_tile_list = import_cut_graphics('./graphics/terrain/terrain_tiles.png')
                        tile_surface = estrutura_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)

                    if type == 'caixote':
                        sprite = Caixote(tile_size,x,y)

                    if type == 'espinhos':
                        sprite = Espinhos(tile_size, x, y)

                    if type == 'moedas':
                        if val == '0': sprite = Moedas(tile_size,x,y,'./graphics/moedas/gold')
                        if val == '1': sprite = Moedas(tile_size,x,y,'./graphics/moedas/silver')

                    if type == 'enemies':
                        sprite = Enemy(tile_size,x,y)

                    if type == 'limite':
                        sprite = Tile(tile_size,x,y)

                    sprite_group.add(sprite)

                return sprite_group

    def player_setup(self,layout):
        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x,y),self.display_surface,self.create_jump_particles)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load('./graphics/character/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size,x,y,hat_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy,self.constraint_sprites,False):
                enemy.reverse()

    def create_jump_particles(self,pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,5)
        else:
            pos += pygame.math.Vector2(10,-5)
            jump_particle_sprite = ParticleEffect(pos,'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        collidable_sprites = self.estrutura_sprites.sprites() + self.caixote_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0: 
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left    
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.estrutura_sprites.sprites() + self.caixote_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0: 
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0.1:
            player.on_ceiling = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(-10,15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset,'land')
            self.dust_sprite.add(fall_dust_particle)

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level,0)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite,self.goal,False):
            self.create_overworld(self.current_level,self.new_max_level)

    def run(self):
		
        # self.input()
        # self.display_surface.blit(self.text_surf, self.text_rect)
		
		# estrutura 
        self.estrutura_sprites.update(self.world_shift)
        self.estrutura_sprites.draw(self.display_surface)
		
		# enemy 
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)

		# caixote 
        self.caixote_sprites.update(self.world_shift)
        self.caixote_sprites.draw(self.display_surface)

		# espinhos
        self.espinhos_sprites.update(self.world_shift)
        self.espinhos_sprites.draw(self.display_surface)
		
		# moedas 
        self.moedas_sprites.update(self.world_shift)
        self.moedas_sprites.draw(self.display_surface)

		# dust particles    
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

		# player sprites
        self.player.update()
        self.horizontal_movement_collision()
		
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
		
        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_death()
        self.check_win
		