from direct.interval.IntervalGlobal import Sequence
from direct.interval.IntervalGlobal import SoundInterval
from direct.task import Task
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import CollideMask
from direct.actor.Actor import Actor
from math import pi, sin, cos


class Main(ShowBase, object):
    def __init__(self):
        super(Main, self).__init__()

        self.load_ttc()

        self.key_map = {'forward': 0, 'backward': 0, 'left': 0, 'right': 0}

        self.player_legs = Actor("phase_3/models/char/tt_a_chr_dgs_shorts_legs_250.bam")
        self.player_torso = Actor("phase_3/models/char/tt_a_chr_dgs_shorts_torso_250.bam")
        self.player_head = Actor("phase_3/models/char/tt_a_chr_dgs_shorts_head_250.bam")

        legs = 'legs'
        torso = 'torso'
        head = 'head'
        self.neutral = 'neutral'
        self.running = 'running'
        self.walk = 'walk'

        parts = {legs: self.player_legs, torso: self.player_torso, head: self.player_head}

        animations = {legs: {self.neutral: "phase_3/models/char/tt_a_chr_dgs_shorts_legs_neutral.bam",
                             self.running: "phase_3/models/char/tt_a_chr_dgs_shorts_legs_run.bam",
                             self.walk: "phase_3.5/models/char/tt_a_chr_dgs_shorts_legs_walk.bam"},
                      torso: {self.neutral: "phase_3/models/char/tt_a_chr_dgs_shorts_torso_neutral.bam",
                              self.running: "phase_3/models/char/tt_a_chr_dgs_shorts_torso_run.bam"},
                      head: {self.neutral: "phase_3/models/char/tt_a_chr_dgs_shorts_head_neutral.bam",
                             self.running: "phase_3/models/char/tt_a_chr_dgs_shorts_head_run.bam"}}

        self.player_body = Actor(parts, animations)

        self.player_body.listJoints(head)
        # Attach our torso and legs to our model's hips.
        self.player_body.attach(torso, legs, 'joint_hips')
        # Attach the head and torso to the model's neck.
        self.player_body.attach(head, torso, 'def_head')
        self.player_body.setPos(0, 0, 5)
        self.player_body.reparentTo(self.render)
        self.player_body.loop(self.neutral)

        self.cog_head = Actor("phase_9/models/char/sellbotBoss-head-zero.bam")
        self.cog_torso = Actor("phase_9/models/char/sellbotBoss-torso-zero.bam")

        cog_torso = 'torso'
        cog_head = 'head'
        cog_neutral = 'neutral'
        self.cog_body = Actor({cog_torso: self.cog_torso, cog_head: self.cog_head},
                              {cog_torso: {cog_neutral: "phase_9/models/char/bossCog-torso-Ff_speech.bam"},
                               cog_head: {cog_neutral: "phase_9/models/char/bossCog-head-Ff_speech.bam"}})

        self.cog_body.listJoints(cog_torso)
        self.cog_body.attach(cog_torso, cog_head, 'joint9_9')
        self.cog_body.setPos(-20, 4, 3)
        self.cog_body.reparentTo(self.render)
        self.cog_body.loop(cog_neutral)

        self.disableMouse()
        # self.create_new_task(self.camera_mover, "Camera mover")
        # self.create_new_task(self.toon_mover, "Toon mover")
        # self.taskMgr.doMethodLater(5, self.toon_mover, 'Toon mover delayed')
        # self.create_new_task(self.sound_stopper, "Sound stopper")

        self.accept('w', self.set_key, ["forward", True])
        self.accept('s', self.set_key, ["backward", True])
        self.accept('a', self.set_key, ["left", True])
        self.accept('d', self.set_key, ["right", True])
        self.accept("w-up", self.set_key, ["forward", False])
        self.accept("s-up", self.set_key, ["backward", False])
        self.accept("a-up", self.set_key, ["left", False])
        self.accept("d-up", self.set_key, ["right", False])

        self.hadle_collisions()

        self.taskMgr.add(self.toon_move, "moveTask")

        # self.accept("a", self.setKey, ["cam-left", True])

        self.is_moving = False

        self.load_and_play_music()

    def create_new_task(self, function_name, name):
        self.taskMgr.add(function_name, name)

    def load_ttc(self):
        self.toontown_central = self.loader.loadModel("phase_4/models/neighborhoods/toontown_central_full.bam")
        self.toontown_central.reparentTo(self.render)

        self.sky = self.loader.loadModel("phase_12/models/bossbotHQ/ttr_m_bossbothq_sky.bam")
        self.sky.reparentTo(self.render)

    def load_and_play_music(self):
        sound1 = self.loader.loadSfx('phase_7/audio/bgm/tt_elevator.ogg')
        sound2 = self.loader.loadSfx('phase_9/audio/bgm/CHQ_FACT_bg.ogg')
        sound3 = self.loader.loadSfx('phase_8/audio/bgm/TB_SZ.ogg')
        sound4 = self.loader.loadSfx('phase_6/audio/bgm/MM_SZ.ogg')
        sound5 = self.loader.loadSfx('phase_13/audio/bgm/party_generic_theme_jazzy.ogg')

        self.music_sequence = Sequence(SoundInterval(sound1), SoundInterval(sound2), SoundInterval(sound3),
                                       SoundInterval(sound4), SoundInterval(sound5), name='Sound Sequence')
        self.music_sequence.loop()

    def camera_mover(self, task):
        angle_radians = (task.time * 50) * (pi / 180)
        self.camera.setPos(0, 0, float(20 * sin(angle_radians) + 5))
        return Task.cont

    def toon_mover(self, task):
        speed = 50
        angle_radians = (task.time * speed) * (pi / 180)

        x = float(200 * cos(5 * angle_radians)) + 8
        y = 0
        z = float(200 * sin(5 * angle_radians)) + 60

        self.player_body.setPos(x, y, z)
        return Task.cont

    def sound_stopper(self, task):
        if self.music_sequence.isPlaying():
            self.music_sequence.finish()
            return Task.done
        else:
            return Task.cont

    # Records keyboard input.
    def set_key(self, key , value):
        self.key_map[key] = value

    def toon_move(self, task):
        # save toons's initial position so that we can restore it,
        # in case he falls off the map or runs into something.
        startpos = self.player_body.getPos()

        # Here, we are setting our camera to follow the player from behind.
        self.camera.setPos(self.player_body.getX(), self.player_body.getY() - 10, 10)
        self.camera.setHpr(0, -15, self.player_body.getR())
        # self.camera.lookAt(self.player_body)

        # This constant will make our player run in a desirable pace.
        dt = .25

        if self.key_map["left"]:
            self.player_body.setH(self.player_body.getH() + 10 * dt)
            print 'left'

        if self.key_map["right"]:
            self.player_body.setH(self.player_body.getH() - 10 * dt)
            print 'right'

        if self.key_map["forward"]:
            self.player_body.setY(self.player_body, 2 * dt)
            print 'forward'

        if self.key_map["backward"]:
            self.player_body.setY(self.player_body, -2 * .1)
            print 'backward'

        if self.key_map["forward"] or self.key_map["left"] or self.key_map["right"]:
            if self.is_moving is False:
                self.player_body.stop()
                self.player_body.loop(self.running)
                print 'moving!'
                self.is_moving = True

        elif self.key_map["backward"]:
            if self.is_moving is False:
                self.player_body.stop()
                self.player_body.loop(self.walk)
                print 'moving -- backwards!'
                self.is_moving = True
        else:
            if self.is_moving:
                self.player_body.stop()
                self.player_body.loop(self.neutral)
                print "neutral!"
                self.is_moving = False

        entries = list(self.player_ground_handler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.player_body.setZ(entries[0].getSurfacePoint(self.render).getZ())
        else:
            pass
        return task.cont

    def hadle_collisions(self):
        self.cTrav = CollisionTraverser()
        self.player_ground_ray = CollisionRay()
        self.player_ground_ray.setOrigin(0, 0, 9)
        self.player_ground_ray.setDirection(0, 0, -1)
        self.player_ground_collider = CollisionNode('PlayerRay')
        self.player_ground_collider.addSolid(self.player_ground_ray)
        self.player_ground_collider.setFromCollideMask(CollideMask.bit(0))
        self.player_ground_collider.setIntoCollideMask(CollideMask.allOff())
        self.player_ground_collision_handle = self.player_body.attachNewNode(self.player_ground_collider)
        self.player_ground_handler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.player_ground_collision_handle, self.player_ground_handler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0, 0, 9)
        self.camGroundRay.setDirection(0, 0, -1)
        self.camGroundCol = CollisionNode('CamRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.camGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.camGroundColNp = self.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

app = Main()
app.run()