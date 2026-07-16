from collections import OrderedDict
import enum





from controls.Switch import Switch
from controls.FileLoader import FileLoader
from controls.Label import Label
from controls.LabelValue import LabelValue
from controls.Button import Button
from controls.Menu import Menu
from controls.DisableMenu import DisableMenu
from controls.MuxMenu import MuxMenu
from controls.SpecialFloatSpinBox import SpecialFloatSpinBox
from controls.LinearIntSliderAndSpinBox import LinearIntSliderAndSpinBox
from controls.LogIntSliderAndSpinBox import LogIntSliderAndSpinBox
from controls.LinearFloatSliderAndSpinBox import LinearFloatSliderAndSpinBox
from controls.SpinBox import SpinBox
from controls.TapMenu import TapMenu
from flowstudio.controls.DiracPage import *
from flowstudio.controls.ListPicker import ListPicker

#########################  I/O  #########################

IN = OrderedDict()

IN_FP = OrderedDict()

INLET = OrderedDict()

OUT = OrderedDict()

OUT_FP = OrderedDict()

OUTLET = OrderedDict()

WAVPLAYER = OrderedDict()
WAVPLAYER['Path'] = FileLoader('Path', [{'Waveform Audio File': ['wav']}])
WAVPLAYER['Gain'] = LinearFloatSliderAndSpinBox('Gain', 0, -120, -3)
WAVPLAYER['Info'] = Label('')

TONEGEN = OrderedDict()
TONEGEN['onoff'] = Switch('onoff', 'on')
TONEGEN['freq'] = LogIntSliderAndSpinBox('freq', 20000, 1, 440)
TONEGEN['gain'] = LinearFloatSliderAndSpinBox('gain', 0, -120, -20)

NOISEGEN = OrderedDict()
NOISEGEN['onoff'] = Switch('onoff', 'on')
NOISEGEN['type'] = Menu('type', ['White Noise', 'Pink Noise'], 'White Noise')
NOISEGEN['gain'] = LinearFloatSliderAndSpinBox('gain', 0, -120, -20)

CHIRP = OrderedDict()
CHIRP['startfreq'] = LogIntSliderAndSpinBox('startfreq', 2000, 10, 20)
CHIRP['endfreq'] = LogIntSliderAndSpinBox('endfreq', 20000, 2000, 20000)
CHIRP['time'] = LinearFloatSliderAndSpinBox('time', 10, 1, 2)
CHIRP['gain'] = LinearFloatSliderAndSpinBox('gain', 0, -120, -20)
CHIRP['mode'] = Menu('mode', ['Linear', 'Log'], 'Log')
CHIRP['trigger'] = Switch('trigger', 'on')

VISUALIZER = OrderedDict()

DUMP = OrderedDict()

FEEDBACK = OrderedDict()

XPATIAL = OrderedDict()
XPATIAL['onoff'] = Switch('onoff', 'on')
XPATIAL['angle'] = LogIntSliderAndSpinBox('angle', 180, 25, 25)
XPATIAL['distance'] = LogIntSliderAndSpinBox('distance', 180, 25, 25)
XPATIAL['brilliance'] = LinearFloatSliderAndSpinBox('brilliance', 10, 0, 0)

CINGO = OrderedDict()
CINGO['EulerUpdate'] = Switch('EulerUpdate', 'off')
CINGO['time'] = LinearIntSliderAndSpinBox('time', 10000, 10, 50)
CINGO['HR'] = Switch('Head Rotation', 'off')
CINGO['HRreset'] = Switch('Auto Euler Reset', 'on')
CINGO['HRtimeTH'] = LinearIntSliderAndSpinBox('Reset Cooldown(ms)', 10000, 0, 5000)
CINGO['HRTimeApply'] = LinearIntSliderAndSpinBox('Reset Apply Time(ms)', 5500, 0, 1200)
CINGO['HRAngleTH'] = LinearIntSliderAndSpinBox('Reset Angle TH', 90, 20, 30)
CINGO['VSP'] = Menu('VSP', ['Non-Spatial(Bypass)', 'Spatial(Headphone)'],
                    'Spatial(Headphone)')
CINGO['VE'] = Menu('Preset',
                   ['STUDIO', 'BOOTH', 'LECTURE_HALL', 'OFFICE', 'CINEMA', 'CHURCH', 'OUTDOOR',
                    'CAVE', 'CAR_PARK', 'ARENA', 'CONCERT_HALL', 'BATHROOM'],
                   'STUDIO')
CINGO['MMpreset'] = Menu('Preset',
                   ['DEFAULT', 'MOVIE', 'MUSIC'],
                   'MUSIC')
CINGO['SmartGain'] = LinearIntSliderAndSpinBox('Smart Gain', 20, -20, 0)
CINGO['FrontAngle'] = LinearIntSliderAndSpinBox('Front Angle', 180, -180, 45)
CINGO['SurroundAngle'] = LinearIntSliderAndSpinBox('Surround Angle', 180, -180, 110)
CINGO['5BandEQEnable'] = Switch('EQ Enable', 'off')
CINGO['5BandEQPreset'] = Menu('EQ Preset',
                   ['NORMAL', 'CLASSICAL', 'DANCE', 'FLAT', 'FOLK', 'METAL', 'HIPHOP',
                    'JAZZ', 'POP', 'ROCK'],
                   'NORMAL')
# CINGO['5BandEQGain'] = LinearIntSliderAndSpinBox('Surround Angle', 12, -12, 0)

CINGO['RoomScale'] = LinearIntSliderAndSpinBox('Room Scale', 100, 0, 50)
CINGO['AbsorptionCurve'] = Menu('Absorption Curve', ['SOFT', 'MEDIUM', 'HARD'], 'MEDIUM')
CINGO['ReverbMix'] = LinearIntSliderAndSpinBox('Reverb Mix', 100, 0, 30)
CINGO['IndivFactor'] = LinearIntSliderAndSpinBox('Individual Factor', 100, 0, 50)
# CINGO['DialogEnable'] = Switch('DialogPlus', 'on')
CINGO['DialogBoost'] = LinearIntSliderAndSpinBox('DialogPlus Boost', 100, 0, 0)
CINGO['ChSpatial_L'] = Switch('Spatial', 'on')
CINGO['ChMute_L'] = Switch('Mute', 'off')
CINGO['ChAzimuth_L'] = LinearIntSliderAndSpinBox('Azimuth Angle', 180, -180, -45)
CINGO['ChElevation_L'] = LinearIntSliderAndSpinBox('Elevation Angle', 90, -90, 0)
CINGO['ChSpatial_R'] = Switch('Spatial', 'on')
CINGO['ChMute_R'] = Switch('Mute', 'off')
CINGO['ChAzimuth_R'] = LinearIntSliderAndSpinBox('Azimuth Angle', 180, -180, 45)
CINGO['ChElevation_R'] = LinearIntSliderAndSpinBox('Elevation Angle', 90, -90, 0)


CINGO_SPK = OrderedDict()
CINGO_SPK['EulerUpdate'] = Switch('EulerUpdate', 'off')
CINGO_SPK['time'] = LinearIntSliderAndSpinBox('time', 10000, 10, 50)
CINGO_SPK['HR'] = Switch('Head Rotation', 'on')
CINGO_SPK['HRreset'] = Switch('Auto Euler Reset', 'on')
CINGO_SPK['HRtimeTH'] = LinearIntSliderAndSpinBox('Reset Cooldown(ms)', 10000, 0, 5000)
CINGO_SPK['HRTimeApply'] = LinearIntSliderAndSpinBox('Reset Apply Time(ms)', 5500, 0, 1200)
CINGO_SPK['HRAngleTH'] = LinearIntSliderAndSpinBox('Reset Angle TH', 90, 20, 30)
CINGO_SPK['VSP'] = Menu('VSP', ['Non-Spatial(Bypass)', 'Spatial(Headphone)', 'Spatial(Speaker)'],
                    'Spatial(Speaker)')
CINGO_SPK['VE'] = Menu('Preset',
                   ['STUDIO', 'BOOTH', 'LECTURE_HALL', 'OFFICE', 'CINEMA', 'CHURCH', 'OUTDOOR',
                    'CAVE', 'CAR_PARK', 'ARENA', 'CONCERT_HALL', 'BATHROOM'],
                   'STUDIO')
CINGO_SPK['RoomScale'] = LinearIntSliderAndSpinBox('Room Scale', 100, 0, 50)
CINGO_SPK['Angle'] = LinearIntSliderAndSpinBox('Speaker Angle', 30, 10, 16)
CINGO_SPK['DynEqCenter'] = LinearFloatSliderAndSpinBox('Dyn EQ Weight Center', 1, 0, 0.4)
CINGO_SPK['DynEqAmb'] = LinearFloatSliderAndSpinBox('Dyn EQ Weight Ambience', 1, 0, 0.4)

CINGO_SPK['AbsorptionCurve'] = Menu('Absorption Curve', ['SOFT', 'MEDIUM', 'HARD'], 'MEDIUM')
CINGO_SPK['ReverbMix'] = LinearIntSliderAndSpinBox('Reverb Mix', 100, 0, 30)
CINGO_SPK['IndivFactor'] = LinearIntSliderAndSpinBox('Individual Factor', 100, 0, 50)
# CINGO_SPK['DialogEnable'] = Switch('DialogPlus', 'on')
CINGO_SPK['DialogBoost'] = LinearIntSliderAndSpinBox('DialogPlus Boost', 100, 0, 0)
CINGO_SPK['ChSpatial_L'] = Switch('Spatial', 'on')
CINGO_SPK['ChMute_L'] = Switch('Mute', 'off')
CINGO_SPK['ChAzimuth_L'] = LinearIntSliderAndSpinBox('Azimuth Angle', 180, -180, -45)
CINGO_SPK['ChElevation_L'] = LinearIntSliderAndSpinBox('Elevation Angle', 90, -90, 0)
CINGO_SPK['ChSpatial_R'] = Switch('Spatial', 'on')
CINGO_SPK['ChMute_R'] = Switch('Mute', 'off')
CINGO_SPK['ChAzimuth_R'] = LinearIntSliderAndSpinBox('Azimuth Angle', 180, -180, 45)
CINGO_SPK['ChElevation_R'] = LinearIntSliderAndSpinBox('Elevation Angle', 90, -90, 0)

ADDER = OrderedDict()

ADDER_FP = OrderedDict()

NEGATOR = OrderedDict()

ABS = OrderedDict()

ABS_FP = OrderedDict()

SQRT = OrderedDict()
SQRT_FP = OrderedDict()

MULTIPLIER = OrderedDict()
MUL_FP = OrderedDict()
SUBTRACTOR = OrderedDict()

RMS = OrderedDict()
RMS['onoff'] = Switch('onoff', 'on')
RMS['rmstime'] = LinearIntSliderAndSpinBox('rmstime', 1000, 0, 0)

MOVAV = OrderedDict()
MOVAV['onoff'] = Switch('onoff', 'on')
MOVAV['sample'] = LinearIntSliderAndSpinBox('sample', 5000, 0, 0)

#########################  FILTERS  #########################

BIQUAD = OrderedDict()
BIQUAD['enable'] = Switch('enable', 'on')
BIQUAD['tap'] = TapMenu({
    'onoff': Switch('onoff', 'on'),
    'a1': LinearFloatSliderAndSpinBox('a1', 3, -3, 0,
                                      is_slider_needed=False, num_decimal_places=10),
    'a2': LinearFloatSliderAndSpinBox('a2', 3, -3, 0,
                                      is_slider_needed=False, num_decimal_places=10),
    'b0': LinearFloatSliderAndSpinBox('b0', 3, -3, 1,
                                      is_slider_needed=False, num_decimal_places=10),
    'b1': LinearFloatSliderAndSpinBox('b1', 3, -3, 0,
                                      is_slider_needed=False, num_decimal_places=10),
    'b2': LinearFloatSliderAndSpinBox('b2', 3, -3, 0,
                                      is_slider_needed=False, num_decimal_places=10),
    'ready': Button('ready', 1, 'send', additional_parameters={ 'label_width': 50,'button_width': 60 })
})

BIQUAD_LOAD = OrderedDict()
BIQUAD_LOAD['num'] = LinearIntSliderAndSpinBox('num of bands', 10000, 0, 1,
                                               additional_parameters={'pRowWidth': [90, 90, 50, 140]})
BIQUAD_LOAD['maxBand'] = LinearIntSliderAndSpinBox('max bands', 10000, 0, 1)

PEQ = OrderedDict()
PEQ['enable'] = Switch('enable', 'on')
PEQ['tap'] = TapMenu({
    'onoff': Switch('onoff', 'on'),
    'kind': Menu('kind', ['low-pass1', 'low-pass2', 'high-pass1', 'high-pass2', 'all-pass1',
                          'all-pass2', 'peaking', 'parametric', 'band-pass', 'notch',
                          'low-shelf', 'high-shelf', 'flat'],
                 'peaking'),
    'fc': LogIntSliderAndSpinBox('fc', 22000, 20, 1000),
    'Q': LinearFloatSliderAndSpinBox('Q', 20.0, 0.10, 4.3),
    'boost': LinearFloatSliderAndSpinBox('boost', 24, -24.0, 0),
    'gain': LinearFloatSliderAndSpinBox('gain', 20, -20.0, 0),
    'slope': LinearFloatSliderAndSpinBox('slope', 1.8, 0.1, 1.414)
})

PEQ_V2 = OrderedDict()
PEQ_V2['enable'] = Switch('enable', 'on')
PEQ_V2['Auto Rescale'] = Switch('Auto Rescale', 'off', additional_parameters={'pRowWidth': [80, 90, 50, 140]})
PEQ_V2['rescale'] = LinearFloatSliderAndSpinBox('rescale', 20.0, -20.0, 0.00,
                                                is_slider_needed=False, num_decimal_places=2,
                                                additional_parameters={'pRowWidth': [80, 90, 50, 140]})
PEQ_V2['tap'] = TapMenu({
    'onoff': Switch('onoff', 'on'),
    'kind': Menu('kind', ['low-pass1', 'low-pass2', 'high-pass1', 'high-pass2', 'all-pass1',
                          'all-pass2', 'peaking', 'parametric', 'band-pass', 'notch',
                          'low-shelf', 'high-shelf', 'flat'],
                 'peaking'),
    'fc': LogIntSliderAndSpinBox('fc', 22000, 20, 1000),
    'Q': LinearFloatSliderAndSpinBox('Q', 20.0, 0.10, 4.3),
    'boost': LinearFloatSliderAndSpinBox('boost', 24, -24.0, 0),
    'gain': LinearFloatSliderAndSpinBox('gain', 20, -20.0, 0),
    'slope': LinearFloatSliderAndSpinBox('slope', 1.8, 0.1, 1.414)
})

PEQ_FP = OrderedDict()
PEQ_FP['enable'] = Switch('enable', 'on')
PEQ_FP['tap'] = TapMenu({
    'onoff': Switch('onoff', 'on'),
    'kind': Menu('kind', ['low-pass1', 'low-pass2', 'high-pass1', 'high-pass2', 'all-pass1',
                          'all-pass2', 'peaking', 'parametric', 'band-pass', 'notch',
                          'low-shelf', 'high-shelf', 'flat'],
                 'peaking'),
    'fc': LogIntSliderAndSpinBox('fc', 22000, 20, 1000),
    'Q': LinearFloatSliderAndSpinBox('Q', 20.0, 0.10, 4.3),
    'boost': LinearFloatSliderAndSpinBox('boost', 24, -24.0, 0),
    'gain': LinearFloatSliderAndSpinBox('gain', 20, -20.0, 0),
    'slope': LinearFloatSliderAndSpinBox('slope', 1.8, 0.1, 1.414)
})

LPF = OrderedDict()
LPF['Enable'] = Switch('Enable', 'on')
LPF['kind'] = Menu('kind', ['Butterworth_6', 'Butterworth_12', 'Butterworth_18', 'Butterworth_24', 'Butterworth_30',
                            'Butterworth_36', 'Bessel_6', 'Bessel_12', 'Bessel_18', 'Bessel_24', 'Bessel_30',
                            'Bessel_36', 'LR_12', 'LR_24', 'LR_36', 'LR_48'],
                   'Butterworth_24')
LPF['fc'] = LogIntSliderAndSpinBox('fc', 22000, 20, 1000)

HPF = OrderedDict()
HPF['Enable'] = Switch('Enable', 'on')
HPF['kind'] = Menu('kind', ['Butterworth_6', 'Butterworth_12', 'Butterworth_18', 'Butterworth_24', 'Butterworth_30',
                            'Butterworth_36', 'Bessel_6', 'Bessel_12', 'Bessel_18', 'Bessel_24', 'Bessel_30',
                            'Bessel_36', 'LR_12', 'LR_24', 'LR_36', 'LR_48'],
                   'Butterworth_24')
HPF['fc'] = LogIntSliderAndSpinBox('fc', 22000, 20, 1000)

HPF_FP = OrderedDict()
HPF_FP['Enable'] = Switch('Enable', 'on')
HPF_FP['kind'] = Menu('kind', ['Butterworth_6', 'Butterworth_12', 'Butterworth_18', 'Butterworth_24', 'Butterworth_30',
                               'Butterworth_36', 'Bessel_6', 'Bessel_12', 'Bessel_18', 'Bessel_24', 'Bessel_30',
                               'Bessel_36', 'LR_12', 'LR_24', 'LR_36', 'LR_48'],
                      'Butterworth_24')
HPF_FP['fc'] = LogIntSliderAndSpinBox('fc', 22000, 20, 1000)

LPF_FP = OrderedDict()
LPF_FP['Enable'] = Switch('Enable', 'on')
LPF_FP['kind'] = Menu('kind', ['Butterworth_6', 'Butterworth_12', 'Butterworth_18', 'Butterworth_24', 'Butterworth_30',
                               'Butterworth_36', 'Bessel_6', 'Bessel_12', 'Bessel_18', 'Bessel_24', 'Bessel_30',
                               'Bessel_36', 'LR_12', 'LR_24', 'LR_36', 'LR_48'],
                      'Butterworth_24')
LPF_FP['fc'] = LogIntSliderAndSpinBox('fc', 22000, 20, 1000)

XOVER = OrderedDict()
XOVER['EnableLF'] = Switch('EnableLF', 'on')
XOVER['EnableHF'] = Switch('EnableHF', 'on')
XOVER['fcLF'] = LogIntSliderAndSpinBox('fcLF', 22000, 20, 1000)
XOVER['fcHF'] = LogIntSliderAndSpinBox('fcHF', 22000, 20, 1000)
XOVER['kindLF'] = Menu('kindLF',
                       ['Butterworth_6', 'Butterworth_12', 'Butterworth_18', 'Butterworth_24', 'Butterworth_30',
                        'Butterworth_36', 'Bessel_6', 'Bessel_12', 'Bessel_18', 'Bessel_24', 'Bessel_30',
                        'Bessel_36', 'LR_12', 'LR_24', 'LR_36', 'LR_48'],
                       'Butterworth_24')
XOVER['kindHF'] = Menu('kindHF',
                       ['Butterworth_6', 'Butterworth_12', 'Butterworth_18', 'Butterworth_24', 'Butterworth_30',
                        'Butterworth_36', 'Bessel_6', 'Bessel_12', 'Bessel_18', 'Bessel_24', 'Bessel_30',
                        'Bessel_36', 'LR_12', 'LR_24', 'LR_36', 'LR_48'],
                       'Butterworth_24')

XOVER_FP = OrderedDict()
XOVER_FP['EnableLF'] = Switch('EnableLF', 'on')
XOVER_FP['EnableHF'] = Switch('EnableHF', 'on')
XOVER_FP['fcLF'] = LogIntSliderAndSpinBox('fcLF', 22000, 20, 1000)
XOVER_FP['fcHF'] = LogIntSliderAndSpinBox('fcHF', 22000, 20, 1000)
XOVER_FP['kindLF'] = Menu('kindLF',
                          ['Butterworth_6', 'Butterworth_12', 'Butterworth_18', 'Butterworth_24', 'Butterworth_30',
                           'Butterworth_36', 'Bessel_6', 'Bessel_12', 'Bessel_18', 'Bessel_24', 'Bessel_30',
                           'Bessel_36', 'LR_12', 'LR_24', 'LR_36', 'LR_48'],
                          'Butterworth_24')
XOVER_FP['kindHF'] = Menu('kindHF',
                          ['Butterworth_6', 'Butterworth_12', 'Butterworth_18', 'Butterworth_24', 'Butterworth_30',
                           'Butterworth_36', 'Bessel_6', 'Bessel_12', 'Bessel_18', 'Bessel_24', 'Bessel_30',
                           'Bessel_36', 'LR_12', 'LR_24', 'LR_36', 'LR_48'],
                          'Butterworth_24')

IIRCOEF = OrderedDict()
IIRCOEF['onoff'] = Switch('onoff', 'on')
IIRCOEF['File'] = FileLoader('File', [{'Filter Coefficient': ['xls', 'xlsx']}])
# IIRCOEF['ready'] = Button('ready', 1)

IIRCOEF_FP = OrderedDict()
IIRCOEF_FP['onoff'] = Switch('onoff', 'on')
IIRCOEF_FP['File'] = FileLoader('File', [{'Filter Coefficient': ['xls', 'xlsx']}])

FIR = OrderedDict()
FIR['onoff'] = Switch('onoff', 'on')
FIR['File'] = FileLoader('File', [{'Filter Coefficient': ['xls', 'xlsx']}])

FIR_FP = OrderedDict()
FIR_FP['onoff'] = Switch('onoff', 'on')
FIR_FP['File'] = FileLoader('File', [{'Filter Coefficient': ['xls', 'xlsx']}])

FIR_LOAD = OrderedDict()
FIR_LOAD['num'] = LinearIntSliderAndSpinBox('num of taps', 10000, 0, 1,
                                            additional_parameters={'pRowWidth': [90, 90, 50, 140]})
FIR_LOAD['maxTap'] = LinearIntSliderAndSpinBox('max taps', 10000, 0, 1)

GAME_EQ = OrderedDict()
GAME_EQ['onoff'] = Switch('onoff', 'on')
GAME_EQ['gameProfile'] = ListPicker('Game Profile',
                          ['AION', 'Alan Wake 2', 'Apex Legends', 'Armored Core VI: Fires of Rubicon', 'Assassin’s Creed Mirage',
                           'Assassin’s Creed Odyssey', 'Assassin’s Creed Origins', 'Assassin’s Creed Origins', 'Atlas Fallen',
                           'Avowed', 'Baldur’s Gate 3', 'Battlefield 2042', 'Black Myth: Wukong', 'Call of Duty: Modern Warfare II',
                           'Call of Duty: Modern Warfare III', 'Call of Duty: Warzone', 'CrossFire', 'CS:GO', 'Cyberpunk 2077',
                           'Darkest Dungeon II', 'DayZ', 'Dead by Daylight', 'Delta Force', 'Destiny 2', 'Diablo IV', 'Dota 2',
                           'Dragon Quest III HD-2D Remake', 'Elden Ring', 'Escape from Tarkov', 'Euro Truck Simulator 2',
                           'Factorio', 'Fall Guys', 'Fallout 76', 'Final Fantasy VII Rebirth', 'Final Fantasy XIV Online',
                           'Final Fantasy XVI', 'Fortnite by FaZe', 'Forza Horizon 5', 'Forza Motorsport', 'Genshin Impact',
                           'Ghost of Tsushima', 'God of War Ragnarök', 'GTA V', 'Halo Infinite', 'Hearthstone', 'Hell Let Loose',
                           'Helldivers 2', 'Hogwarts Legacy', 'League of Legends', 'Left 4 Dead 2', 'Like a Dragon:Infinite Wealth',
                           'Like a Dragon:Pirate Yakuza in Hawaii', 'Marvel Rivals', "Marvel's Spider-Man 2", 'Minecraft',
                           'Monster Hunter World', 'Mortal Kombat 1', 'NBA 2K24', 'Once Human', 'Palworld', 'PEAK',
                           'PUBG:BATTLEGROUNDS', 'R.E.P.O.', 'Raft', 'Rainbow Six Siege', 'REMATCH', 'Resident Evil Village',
                           'Roblox', 'Rust', 'Silent Hill 2', 'Star Wars Battlefront II', 'Star Wars Jedi: Survivor',
                           'Star Wars Jedi: Survivor', 'Stellar Blade', 'Street Fighter 6', 'Team Fortress 2', 'The Division 2',
                           'The Elder Scrolls Online', 'The Last Of Us', 'The Last Of Us Part II', 'The Witcher 3: Wild Hunt',
                           'Valorant', 'Vampire: The Masquerade - Bloodhunt', 'Warframe', 'Warhammer 40,000: Boltgun',
                           'Warhammer 40,000: Space Marine 2', 'World of Tanks', 'World of Warcraft', 'Xdefiant',
                           'Zenless Zone Zero'], 0)

CustomEQ = OrderedDict()
CustomEQ['onoff'] = Switch('onoff', 'on')
CustomEQ['Presets'] = ListPicker('Game Profile',
                          ['Custom','Normal','Classical','Dance','Flat','Folk','Metal','Hip Hop','Jazz','Pop','Rock','AION', 'Alan Wake 2', 'Apex Legends', 'Armored Core VI: Fires of Rubicon', 'Assassin’s Creed Mirage',
                           'Assassin’s Creed Odyssey', 'Assassin’s Creed Origins', 'Assassin’s Creed Origins', 'Atlas Fallen',
                           'Avowed', 'Baldur’s Gate 3', 'Battlefield 2042', 'Black Myth: Wukong', 'Call of Duty: Modern Warfare II',
                           'Call of Duty: Modern Warfare III', 'Call of Duty: Warzone', 'CrossFire', 'CS:GO', 'Cyberpunk 2077',
                           'Darkest Dungeon II', 'DayZ', 'Dead by Daylight', 'Delta Force', 'Destiny 2', 'Diablo IV', 'Dota 2',
                           'Dragon Quest III HD-2D Remake', 'Elden Ring', 'Escape from Tarkov', 'Euro Truck Simulator 2',
                           'Factorio', 'Fall Guys', 'Fallout 76', 'Final Fantasy VII Rebirth', 'Final Fantasy XIV Online',
                           'Final Fantasy XVI', 'Fortnite by FaZe', 'Forza Horizon 5', 'Forza Motorsport', 'Genshin Impact',
                           'Ghost of Tsushima', 'God of War Ragnarök', 'GTA V', 'Halo Infinite', 'Hearthstone', 'Hell Let Loose',
                           'Helldivers 2', 'Hogwarts Legacy', 'League of Legends', 'Left 4 Dead 2', 'Like a Dragon:Infinite Wealth',
                           'Like a Dragon:Pirate Yakuza in Hawaii', 'Marvel Rivals', "Marvel's Spider-Man 2", 'Minecraft',
                           'Monster Hunter World', 'Mortal Kombat 1', 'NBA 2K24', 'Once Human', 'Palworld', 'PEAK',
                           'PUBG:BATTLEGROUNDS', 'R.E.P.O.', 'Raft', 'Rainbow Six Siege', 'REMATCH', 'Resident Evil Village',
                           'Roblox', 'Rust', 'Silent Hill 2', 'Star Wars Battlefront II', 'Star Wars Jedi: Survivor',
                           'Star Wars Jedi: Survivor', 'Stellar Blade', 'Street Fighter 6', 'Team Fortress 2', 'The Division 2',
                           'The Elder Scrolls Online', 'The Last Of Us', 'The Last Of Us Part II', 'The Witcher 3: Wild Hunt',
                           'Valorant', 'Vampire: The Masquerade - Bloodhunt', 'Warframe', 'Warhammer 40,000: Boltgun',
                           'Warhammer 40,000: Space Marine 2', 'World of Tanks', 'World of Warcraft', 'Xdefiant',
                           'Zenless Zone Zero', 'News', 'Bass'], 0)
CustomEQ['band30'] = LinearFloatSliderAndSpinBox('band30', 20, -20, 0)
CustomEQ['band60'] = LinearFloatSliderAndSpinBox('band60', 20, -20, 0)
CustomEQ['band120'] = LinearFloatSliderAndSpinBox('band120', 20, -20, 0)
CustomEQ['band250'] = LinearFloatSliderAndSpinBox('band250', 20, -20, 0)
CustomEQ['band500'] = LinearFloatSliderAndSpinBox('band500', 20, -20, 0)
CustomEQ['band1K'] = LinearFloatSliderAndSpinBox('band1K', 20, -20, 0)
CustomEQ['band2K'] = LinearFloatSliderAndSpinBox('band2K', 20, -20, 0)
CustomEQ['band4K'] = LinearFloatSliderAndSpinBox('band4K', 20, -20, 0)
CustomEQ['band8K'] = LinearFloatSliderAndSpinBox('band8K', 20, -20, 0)
CustomEQ['band16K'] = LinearFloatSliderAndSpinBox('band16K', 20, -20, 0)

LMS = OrderedDict()
LMS['onoff'] = Switch('onoff', 'on')
LMS['freeze'] = Switch('freeze', 'on')
LMS['kind'] = Menu('kind', ['LMS', 'NLMS'], 'LMS')
LMS['ntaps'] = LinearIntSliderAndSpinBox('ntaps', 256, 5, 16)
LMS['mu'] = LinearFloatSliderAndSpinBox('mu', 1, 0.0001, 0.0001)
LMS['leakage'] = LinearFloatSliderAndSpinBox('leakage', 1, 0.0001, 0.0001)
LMS['epsilon'] = LinearFloatSliderAndSpinBox('epsilon', 1, 0.0001, 0)

#########################  GAINS  #########################

GAIN = OrderedDict()
GAIN['gain'] = LinearFloatSliderAndSpinBox('gain(dB)', 24, -120, 0,
                                           orientation='vertical', has_buttons=True)

GAIN_FP = OrderedDict()
GAIN_FP['gain'] = LinearFloatSliderAndSpinBox('gain(dB)', 24, -120, 0,
                                              orientation='vertical', has_buttons=True)

GAIN_ST = OrderedDict()
GAIN_ST['gain'] = LinearFloatSliderAndSpinBox('gain(dB)', 24, -120, 0)

SMART_GAIN = OrderedDict()
SMART_GAIN['range'] = LinearFloatSliderAndSpinBox('range', 24, 0, 8)
SMART_GAIN['target'] = LinearFloatSliderAndSpinBox('target', 0, -24, -8)
SMART_GAIN['onoff'] = SpecialFloatSpinBox('onoff', 1, 0, 0)

ATTEN = OrderedDict()
ATTEN['gain'] = LinearFloatSliderAndSpinBox('gain(lin)', 1, 0, 1)

ATTEN_ST = OrderedDict()
ATTEN_ST['gain'] = LinearFloatSliderAndSpinBox('gain(lin)', 1, 0, 1)

MUTE = OrderedDict()
MUTE['mute'] = Switch('mute', 'on')

MUTE_FP = OrderedDict()
MUTE_FP['mute'] = Switch('mute', 'on')

LOUDNESS = OrderedDict()
LOUDNESS['onoff'] = Switch('onoff', 'on')
LOUDNESS['gain'] = LinearFloatSliderAndSpinBox('gain(dB)', 0, -60, 0)
LOUDNESS['maxSPL'] = LinearFloatSliderAndSpinBox('maxSPL', 100, 80, 80)

POLARITY = OrderedDict()
POLARITY['polarity'] = Switch('polarity', 'off')

QUICK_GAIN = OrderedDict()
QUICK_GAIN['onoff'] = Switch('onoff', 'on')
QUICK_GAIN['targetLUFS'] = LinearIntSliderAndSpinBox('Target LUFS', 0, -40, -23)
QUICK_GAIN['recTime'] = LinearIntSliderAndSpinBox('Rec Time', 20, 1, 5)
QUICK_GAIN['minThreshold'] = LinearIntSliderAndSpinBox('BG Noise Level', -40, -70, -60)
QUICK_GAIN['resetGain'] = Button('', 0, 'Reset Gain', additional_parameters={ 'label_width': 0,'button_width': 252 })
QUICK_GAIN['startRec'] = Button('', 0, 'Start Rec', additional_parameters={ 'label_width': 0,'button_width': 252 })

#########################  DYNAMICS  #########################

LIMITER = OrderedDict()
LIMITER['onoff'] = Switch('onoff', 'on')
LIMITER['type'] = Menu('type', ['RMS', 'Peak'], 'RMS')
LIMITER['knee'] = LinearFloatSliderAndSpinBox('knee', 24, 0, 0)
LIMITER['threshold'] = LinearFloatSliderAndSpinBox('threshold', 0, -100, 0)
LIMITER['ta'] = LinearFloatSliderAndSpinBox('ta', 250, 0.01, 1)
LIMITER['hold'] = LinearFloatSliderAndSpinBox('hold', 500, 0, 0)
LIMITER['td'] = LinearFloatSliderAndSpinBox('td', 5, 0, 0)
LIMITER['te'] = LinearFloatSliderAndSpinBox('te', 200, 10, 10)
LIMITER['tr'] = LinearFloatSliderAndSpinBox('tr', 2500, 1, 50)
LIMITER['makeup'] = LinearFloatSliderAndSpinBox('makeup', 32, 0, 0)

LIMITER_FP = OrderedDict()
LIMITER_FP['onoff'] = Switch('onoff', 'on')
LIMITER_FP['type'] = Menu('type', ['RMS', 'Peak'], 'RMS')
LIMITER_FP['knee'] = LinearFloatSliderAndSpinBox('knee', 24, 0, 0)
LIMITER_FP['threshold'] = LinearFloatSliderAndSpinBox('threshold', 0, -50, 0)
LIMITER_FP['td'] = LinearFloatSliderAndSpinBox('td', 5, 0, 0)
LIMITER_FP['te'] = LinearFloatSliderAndSpinBox('te', 300, 10, 10)
LIMITER_FP['ta'] = LinearFloatSliderAndSpinBox('ta', 250, 0.01, 1)
LIMITER_FP['tr'] = LinearFloatSliderAndSpinBox('tr', 2500, 1, 50)
LIMITER_FP['makeup'] = LinearFloatSliderAndSpinBox('makeup', 32, 0, 0)

COMP = OrderedDict()
COMP['onoff'] = Switch('onoff', 'on')
COMP['type'] = Menu('type', ['RMS', 'Peak'], 'RMS')
COMP['knee'] = LinearFloatSliderAndSpinBox('knee', 24, 0, 0)
COMP['thres'] = LinearFloatSliderAndSpinBox('thres', 0, -90, 0)
COMP['ratio'] = LinearFloatSliderAndSpinBox('ratio', 100, 1, 1)
COMP['ta'] = LinearFloatSliderAndSpinBox('ta', 250, 0.01, 1)
COMP['hold'] = LinearFloatSliderAndSpinBox('hold', 500, 0, 0)
COMP['td'] = LinearFloatSliderAndSpinBox('td', 5, 0, 0)
COMP['te'] = LinearFloatSliderAndSpinBox('te', 300, 1, 1)
COMP['tr'] = LinearFloatSliderAndSpinBox('tr', 2500, 1, 10)
COMP['makeup'] = LinearFloatSliderAndSpinBox('makeup', 32, 0, 0)

COMP_FP = OrderedDict()
COMP_FP['onoff'] = Switch('onoff', 'on')
COMP_FP['type'] = Menu('type', ['RMS', 'Peak'], 'RMS')
COMP_FP['knee'] = LinearFloatSliderAndSpinBox('knee', 24, 0, 0)
COMP_FP['thres'] = LinearFloatSliderAndSpinBox('thres', 0, -50, 0)
COMP_FP['ratio'] = LinearFloatSliderAndSpinBox('ratio', 16, 1, 1)
COMP_FP['td'] = LinearFloatSliderAndSpinBox('td', 5, 0, 0)
COMP_FP['te'] = LinearFloatSliderAndSpinBox('te', 300, 1, 1)
COMP_FP['ta'] = LinearFloatSliderAndSpinBox('ta', 250, 0.01, 1)
COMP_FP['tr'] = LinearFloatSliderAndSpinBox('tr', 2500, 1, 10)
COMP_FP['makeup'] = LinearFloatSliderAndSpinBox('makeup', 32, 0, 0)

COMP_Combo = OrderedDict()
COMP_Combo['onoff'] = Switch('onoff', 'on')
COMP_Combo['thres1'] = LinearFloatSliderAndSpinBox('thres1', -30, -90, -90)
COMP_Combo['thres2'] = LinearFloatSliderAndSpinBox('thres2', 20, -70, -30)
COMP_Combo['noisegate'] = LinearFloatSliderAndSpinBox('noisegate', -90, -120, -120)
COMP_Combo['ratio0'] = LinearFloatSliderAndSpinBox('ratio0', 16, 1, 1)
COMP_Combo['ratio1'] = LinearFloatSliderAndSpinBox('ratio1', 16, 1, 1)
COMP_Combo['ratio2'] = LinearFloatSliderAndSpinBox('ratio2', 16, 1, 1)
COMP_Combo['type'] = Menu('type', ['RMS', 'Peak'], 'RMS')
COMP_Combo['ta'] = LinearFloatSliderAndSpinBox('ta', 250, 0.01, 1)
COMP_Combo['td'] = LinearFloatSliderAndSpinBox('td', 5, 0, 0)
COMP_Combo['te'] = LinearFloatSliderAndSpinBox('te', 300, 1, 1)
COMP_Combo['tr'] = LinearFloatSliderAndSpinBox('tr', 2500, 1, 1)
COMP_Combo['hold'] = LinearFloatSliderAndSpinBox('hold', 500, 0, 0)
COMP_Combo['makeup'] = LinearFloatSliderAndSpinBox('makeup', 32, 0, 0)

COMP_Combo_FP = OrderedDict()
COMP_Combo_FP['onoff'] = Switch('onoff', 'on')
COMP_Combo_FP['thres1'] = LinearFloatSliderAndSpinBox('thres1', -30, -90, -90)
COMP_Combo_FP['thres2'] = LinearFloatSliderAndSpinBox('thres2', 20, -70, -30)
COMP_Combo_FP['noisegate'] = LinearFloatSliderAndSpinBox('noisegate', -90, -120, -120)
COMP_Combo_FP['ratio0'] = LinearFloatSliderAndSpinBox('ratio0', 16, 1, 1)
COMP_Combo_FP['ratio1'] = LinearFloatSliderAndSpinBox('ratio1', 16, 1, 1)
COMP_Combo_FP['ratio2'] = LinearFloatSliderAndSpinBox('ratio2', 16, 1, 1)
COMP_Combo_FP['type'] = Menu('type', ['RMS', 'Peak'], 'RMS')
COMP_Combo_FP['ta'] = LinearFloatSliderAndSpinBox('ta', 250, 0.01, 1)
COMP_Combo_FP['td'] = LinearFloatSliderAndSpinBox('td', 5, 0, 0)
COMP_Combo_FP['te'] = LinearFloatSliderAndSpinBox('te', 300, 1, 1)
COMP_Combo_FP['tr'] = LinearFloatSliderAndSpinBox('tr', 2500, 1, 1)
COMP_Combo_FP['hold'] = LinearFloatSliderAndSpinBox('hold', 500, 0, 0)
COMP_Combo_FP['makeup'] = LinearFloatSliderAndSpinBox('makeup', 32, 0, 0)

AUTO_COMP = OrderedDict()
AUTO_COMP['onoff'] = Switch('onoff', 'on')
AUTO_COMP['type'] = Menu('type', ['RMS', 'Peak'], 'RMS')
AUTO_COMP['knee'] = LinearFloatSliderAndSpinBox('knee', 24, 0, 0)
AUTO_COMP['thres'] = LinearFloatSliderAndSpinBox('thres', 24, -90, 0)
AUTO_COMP['ratio'] = LinearFloatSliderAndSpinBox('ratio', 16, 1, 1)
AUTO_COMP['ta'] = LinearFloatSliderAndSpinBox('ta', 2000, 0.1, 1)
AUTO_COMP['hold'] = LinearFloatSliderAndSpinBox('hold', 100, 0, 0)
AUTO_COMP['td'] = LinearFloatSliderAndSpinBox('td', 10, 0, 0)
AUTO_COMP['te'] = LinearFloatSliderAndSpinBox('te', 500, 0.1, 1)
AUTO_COMP['tr'] = LinearFloatSliderAndSpinBox('tr', 5000, 1, 10)
AUTO_COMP['makeup'] = LinearFloatSliderAndSpinBox('makeup', 32, 0, 0)
AUTO_COMP['attmode'] = Menu('attmode', ['Auto', 'Fixed'], 'Auto')
AUTO_COMP['relmode'] = Menu('relmode', ['Auto', 'Fixed'], 'Auto')
AUTO_COMP['mkupmode'] = Menu('mkupmode', ['Auto', 'Fixed'], 'Auto')

CLIPPER = OrderedDict()
CLIPPER['onoff'] = Switch('onoff', 'on')
CLIPPER['Type'] = Menu('Type', ['soft', 'hard'], 'hard')
CLIPPER['threshold'] = LinearFloatSliderAndSpinBox('threshold', 1, 0, 0.5)

CLIPPER_FP = OrderedDict()
CLIPPER_FP['onoff'] = Switch('onoff', 'on')
# CLIPPER_FP['Type'] = Menu('Type', ['soft', 'hard'], 'hard')
CLIPPER_FP['threshold'] = LinearFloatSliderAndSpinBox('threshold', 1, 0, 0.5)

LIMITER_MB = OrderedDict()
LIMITER_MB['EnableLF'] = Switch('EnableLF', 'on')
LIMITER_MB['EnableHF'] = Switch('EnableHF', 'on')
LIMITER_MB['fc'] = LogIntSliderAndSpinBox('fc', 20000, 20, 1000)

LIMITER_MB['typeLF'] = Menu('type', ['RMS', 'Peak'], 'RMS')
LIMITER_MB['kneeLF'] = LinearFloatSliderAndSpinBox('kneeLF', 24, 0, 0)
LIMITER_MB['thresholdLF'] = LinearFloatSliderAndSpinBox('thresholdLF', 0, -100, 0)
LIMITER_MB['taLF'] = LinearFloatSliderAndSpinBox('taLF', 250, 0.01, 1)
LIMITER_MB['holdLF'] = LinearFloatSliderAndSpinBox('holdLF', 500, 0, 0)
LIMITER_MB['tdLF'] = LinearFloatSliderAndSpinBox('tdLF', 5, 0, 1)
LIMITER_MB['teLF'] = LinearFloatSliderAndSpinBox('teLF', 300, 10, 10)
LIMITER_MB['trLF'] = LinearFloatSliderAndSpinBox('trLF', 2500, 1, 1)
LIMITER_MB['makeupLF'] = LinearFloatSliderAndSpinBox('makeupLF', 32, 0, 0)
LIMITER_MB['typeHF'] = Menu('type', ['RMS', 'Peak'], 'RMS')
LIMITER_MB['kneeHF'] = LinearFloatSliderAndSpinBox('kneeHF', 24, 0, 0)
LIMITER_MB['thresholdHF'] = LinearFloatSliderAndSpinBox('thresholdHF', 0, -100, 0)
LIMITER_MB['taHF'] = LinearFloatSliderAndSpinBox('taHF', 250, 0.01, 1)
LIMITER_MB['holdHF'] = LinearFloatSliderAndSpinBox('holdHF', 500, 0, 0)
LIMITER_MB['tdHF'] = LinearFloatSliderAndSpinBox('tdHF', 5, 0, 1)
LIMITER_MB['teHF'] = LinearFloatSliderAndSpinBox('teHF', 300, 1, 1)
LIMITER_MB['trHF'] = LinearFloatSliderAndSpinBox('trHF', 2500, 1, 1)
LIMITER_MB['makeupHF'] = LinearFloatSliderAndSpinBox('makeupHF', 32, 0, 0)

GATE = OrderedDict()
GATE['onoff'] = Switch('onoff', 'on')
GATE['type'] = Menu('type', ['RMS', 'Peak'], 'RMS')
GATE['knee'] = LinearFloatSliderAndSpinBox('knee', 24, 0, 0)
GATE['thres'] = LinearFloatSliderAndSpinBox('thres', 0, -120, -90)
GATE['ratio'] = LinearFloatSliderAndSpinBox('ratio', 24, 1, 1)
GATE['ta'] = LinearFloatSliderAndSpinBox('ta', 2000, 0.1, 10)
GATE['hold'] = LinearFloatSliderAndSpinBox('hold', 100, 0, 0)
GATE['td'] = LinearFloatSliderAndSpinBox('td', 10, 0, 0)
GATE['te'] = LinearFloatSliderAndSpinBox('te', 500, 0.1, 1)
GATE['tr'] = LinearFloatSliderAndSpinBox('tr', 5000, 1, 100)

SMART_GATE = OrderedDict()
SMART_GATE['onoff'] = Switch('onoff', 'on')
SMART_GATE['type'] = Menu('type', ['RMS', 'Peak'], 'RMS')
SMART_GATE['knee'] = LinearFloatSliderAndSpinBox('knee', 24, 0, 0)
SMART_GATE['ratio'] = LinearFloatSliderAndSpinBox('ratio', 24, 1, 1)
SMART_GATE['ta'] = LinearFloatSliderAndSpinBox('ta', 2000, 0.1, 10)
SMART_GATE['hold'] = LinearFloatSliderAndSpinBox('hold', 100, 0, 0)
SMART_GATE['td'] = LinearFloatSliderAndSpinBox('td', 10, 0, 0)
SMART_GATE['te'] = LinearFloatSliderAndSpinBox('te', 500, 0.1, 1)
SMART_GATE['tr'] = LinearFloatSliderAndSpinBox('tr', 5000, 1, 100)
SMART_GATE['thres'] = LinearFloatSliderAndSpinBox('thres', 0, -120, -90)

DYNAMIC_FILTER = OrderedDict()
DYNAMIC_FILTER['onoff'] = Switch('onoff', 'on')
DYNAMIC_FILTER['HiThresh'] = LinearFloatSliderAndSpinBox('HiThresh', 1, 0, 0.00015,
                                                         additional_parameters={'pDecimalPrecision': 5,
                                                                                'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['LowThresh'] = LinearFloatSliderAndSpinBox('LowThresh', 1, 0, 0.0006,
                                                          additional_parameters={'pDecimalPrecision': 5,
                                                                                 'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['ta'] = LinearFloatSliderAndSpinBox('ta', 2000, 0.1, 100,
                                                   additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['hold'] = LinearFloatSliderAndSpinBox('hold', 100, 0, 50,
                                                     additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['te'] = LinearFloatSliderAndSpinBox('te', 500, 0.1, 1,
                                                   additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['tr'] = LinearFloatSliderAndSpinBox('tr', 5000, 1, 50,
                                                   additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['fc'] = LogIntSliderAndSpinBox('fc', 22000, 20, 100,
                                              additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['LowFc'] = LogIntSliderAndSpinBox('LowFc', 22000, 20, 25,
                                                 additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['LowPeakFc'] = LogIntSliderAndSpinBox('LowPeakFc', 22000, 20, 80,
                                                     additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['boostL'] = LinearFloatSliderAndSpinBox('boostL', 24, -24.0, 6,
                                                       additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['QL'] = LinearFloatSliderAndSpinBox('QL', 20.0, 0.10, 2,
                                                   additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['HiFc'] = LogIntSliderAndSpinBox('HiFc', 22000, 20, 45,
                                                additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['HiPeakFc'] = LogIntSliderAndSpinBox('HiPeakFc', 22000, 20, 120,
                                                    additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['boostH'] = LinearFloatSliderAndSpinBox('boostH', 24, -24.0, 6,
                                                       additional_parameters={'pRowWidth': [60, 90, 50, 140]})
DYNAMIC_FILTER['QH'] = LinearFloatSliderAndSpinBox('QH', 20.0, 0.10, 2,
                                                   additional_parameters={'pRowWidth': [60, 90, 50, 140]})

#########################  ROUTINGS  #########################

MERGER = OrderedDict()

MIXER8 = OrderedDict()
MIXER8['MixGain_0'] = LinearFloatSliderAndSpinBox('gain1', 24, -120, 0)
MIXER8['MixGain_1'] = LinearFloatSliderAndSpinBox('gain2', 24, -120, 0)
MIXER8['MixGain_2'] = LinearFloatSliderAndSpinBox('gain3', 24, -120, 0)
MIXER8['MixGain_3'] = LinearFloatSliderAndSpinBox('gain4', 24, -120, 0)
MIXER8['MixGain_4'] = LinearFloatSliderAndSpinBox('gain5', 24, -120, 0)
MIXER8['MixGain_5'] = LinearFloatSliderAndSpinBox('gain6', 24, -120, 0)
MIXER8['MixGain_6'] = LinearFloatSliderAndSpinBox('gain7', 24, -120, 0)
MIXER8['MixGain_7'] = LinearFloatSliderAndSpinBox('gain8', 24, -120, 0)

MIXER = OrderedDict()
MIXER['tap'] = TapMenu({
    'MixGain_0': LinearFloatSliderAndSpinBox('gain 1', 24, -120, 0),
    'MixGain_1': LinearFloatSliderAndSpinBox('gain 2', 24, -120, 0),
    'MixGain_2': LinearFloatSliderAndSpinBox('gain 3', 24, -120, 0),
    'MixGain_3': LinearFloatSliderAndSpinBox('gain 4', 24, -120, 0),
    'MixGain_4': LinearFloatSliderAndSpinBox('gain 5', 24, -120, 0),
    'MixGain_5': LinearFloatSliderAndSpinBox('gain 6', 24, -120, 0),
    'MixGain_6': LinearFloatSliderAndSpinBox('gain 7', 24, -120, 0),
    'MixGain_7': LinearFloatSliderAndSpinBox('gain 8', 24, -120, 0)
})

MIXER_FP = OrderedDict()
MIXER_FP['tap'] = TapMenu({
    'MixGain_0': LinearFloatSliderAndSpinBox('gain 1', 24, -120, 0),
    'MixGain_1': LinearFloatSliderAndSpinBox('gain 2', 24, -120, 0),
    'MixGain_2': LinearFloatSliderAndSpinBox('gain 3', 24, -120, 0),
    'MixGain_3': LinearFloatSliderAndSpinBox('gain 4', 24, -120, 0),
    'MixGain_4': LinearFloatSliderAndSpinBox('gain 5', 24, -120, 0),
    'MixGain_5': LinearFloatSliderAndSpinBox('gain 6', 24, -120, 0),
    'MixGain_6': LinearFloatSliderAndSpinBox('gain 7', 24, -120, 0),
    'MixGain_7': LinearFloatSliderAndSpinBox('gain 8', 24, -120, 0)
})

MUX = OrderedDict()
MUX['select'] = MuxMenu('select', ['Ch 1', 'Ch 2', 'Ch 3', 'Ch 4', 'Ch 5', 'Ch 6', 'Ch 7', 'Ch 8'],
                        'Ch 1')

MUX_FP = OrderedDict()
MUX_FP['select'] = Menu('select', ['Ch 1', 'Ch 2', 'Ch 3', 'Ch 4', 'Ch 5', 'Ch 6', 'Ch 7', 'Ch 8'],
                        'Ch 1')

MUX_ST = OrderedDict()
MUX_ST['select'] = Menu('select', ['Ch 1,2', 'Ch 3,4', 'Ch 5,6', 'Ch 7,8'],
                        'Ch 1,2')

DRYWET = OrderedDict()
DRYWET['mix'] = LinearFloatSliderAndSpinBox('mix', 1, 0, 0.5)

#########################  EFFECTS  #########################

DELAY = OrderedDict()
DELAY['onoff'] = Switch('onoff', 'on')
DELAY['time'] = LinearIntSliderAndSpinBox('samples', 1000, 0, 0)

DELAY_FP = OrderedDict()
DELAY_FP['onoff'] = Switch('onoff', 'on')
DELAY_FP['time'] = LinearIntSliderAndSpinBox('samples', 1000, 0, 0)

DELAY_Intp = OrderedDict()
DELAY_Intp['onoff'] = Switch('onoff', 'on')
DELAY_Intp['time'] = LinearFloatSliderAndSpinBox('time', 8192, 1, 1000)

MULTITAP = OrderedDict()
MULTITAP['onoff'] = Switch('onoff', 'on')
MULTITAP['mix'] = LinearFloatSliderAndSpinBox('mix', 1, 0, 0.5)
MULTITAP['tap'] = TapMenu({
    'time': LinearIntSliderAndSpinBox('time', 1024, 1, 1),
    'gain': LinearFloatSliderAndSpinBox('gain', 1, 0, 0.5)
})

LONG_APF = OrderedDict()
LONG_APF['onoff'] = Switch('onoff', 'on')
LONG_APF['tap'] = TapMenu({
    'time': LinearIntSliderAndSpinBox('time', 2048, 1, 512),
    'gain': LinearFloatSliderAndSpinBox('gain', 1, 0, 0.7)
})

LPF_COMB_FILTER = OrderedDict()
LPF_COMB_FILTER['onoff'] = Switch('onoff', 'on')
LPF_COMB_FILTER['tap'] = TapMenu({
    'time': LinearIntSliderAndSpinBox('time', 4096, 1, 1000),
    'damp': LinearFloatSliderAndSpinBox('damp', 1, 0, 0.2),
    'roomsize': LinearFloatSliderAndSpinBox('roomsize', 1, 0, 0.5)
})

# REVERB = OrderedDict()
# REVERB['onoff'] = Switch('onoff', 'on')
# REVERB['mix'] = LinearFloatSliderAndSpinBox('mix', 1, 0, 0.5)
# REVERB['kind'] = Menu('kind', ['ideal', 'small', 'dre verb', 'large choir hall', 'boston symphony hall', 'new york philharmonic hall'], 'ideal')
# REVERB['roomsize'] = LinearFloatSliderAndSpinBox('roomsize', 1, 0, 0.5)
# REVERB['damp'] = LinearFloatSliderAndSpinBox('damp', 1, 0, 0.5)
# REVERB['diffusion'] = LinearFloatSliderAndSpinBox('diffusion', 0.95, 0, 0.707)

REVERB_V2 = OrderedDict()
REVERB_V2['onoff'] = Switch('onoff', 'on')
REVERB_V2['mix'] = LinearFloatSliderAndSpinBox('mix', 1, 0, 0.5)
REVERB_V2['roomsize'] = LinearFloatSliderAndSpinBox('roomsize', 1, 0, 0.8)
REVERB_V2['damp'] = LinearFloatSliderAndSpinBox('damp', 1, 0, 0.15)

CHORUS = OrderedDict()
CHORUS['onoff'] = Switch('onoff', 'on')
CHORUS['mix'] = LinearFloatSliderAndSpinBox('mix', 1, 0, 0.5)
CHORUS['rate'] = LinearFloatSliderAndSpinBox('rate', 5, 0.1, 0.5)
CHORUS['depth'] = LinearFloatSliderAndSpinBox('depth', 1, 0, 0.25)

DIRAC = OrderedDict()
DIRAC['configure'] = DiracMenu('configure', ['2.0', '5.1.2', '7.1.4'])
DIRAC['username'] = DiracEdit('username', 'root')
DIRAC['password'] = DiracEdit('password', '123456')
DIRAC['devicename'] = DiracEdit('device name', 'device')
DIRAC['infotab'] = DiracTab()
DIRAC['inputinfo'] = DiracInputInfo()
DIRAC['speakerinfo'] = DiracSpeakerInfo()

######################  Proprietary  ######################

VAD = OrderedDict()
VAD['onoff'] = Switch('onoff', 'on')
VAD['thres'] = LinearFloatSliderAndSpinBox('thres', 1.0, 0.0, 0.95)
VAD['ratio'] = LinearFloatSliderAndSpinBox('ratio', 1.0, 0.0, 0.9)

VAD_IABSE = OrderedDict()
VAD_IABSE['onoff'] = Switch('onoff', 'on')
VAD_IABSE['Sensit'] = LinearIntSliderAndSpinBox('Sensit', 10, 1, 4)

ROOM_FIX = OrderedDict()
ROOM_FIX['onoff'] = Switch('onoff', 'on')
ROOM_FIX['freeze'] = Switch('freeze', 'off')
ROOM_FIX['reset'] = Switch('reset', 'off')
ROOM_FIX['fsboost'] = LinearFloatSliderAndSpinBox('fsboost', 100, 0, 8.0)
ROOM_FIX['ta'] = LinearFloatSliderAndSpinBox('ta', 1000000, 0, 2266.8)
ROOM_FIX['tr'] = LinearFloatSliderAndSpinBox('tr', 1000000, 0.1, 2266.8)
ROOM_FIX['tf'] = LinearFloatSliderAndSpinBox('tf', 1000000, 0.1, 2266.8)
ROOM_FIX['fc'] = LinearFloatSliderAndSpinBox('fc', 22000, 20, 200)
ROOM_FIX['slope'] = LinearFloatSliderAndSpinBox('slope', 1.8, 0.1, 0.707)
ROOM_FIX['effthold'] = LinearFloatSliderAndSpinBox('effthold', 1.0, 0, 0.0001)

DEESSER = OrderedDict()
DEESSER['onoff'] = Switch('onoff', 'on')
DEESSER['thres'] = LinearFloatSliderAndSpinBox('thres', 0, -20, -3)
DEESSER['ratio'] = LinearFloatSliderAndSpinBox('ratio', 8, 1, 2)
DEESSER['fc'] = Menu('fc', ['4k', '5k', '6k'], '4k')
DEESSER['ta'] = LinearFloatSliderAndSpinBox('ta', 200, 0.1, 10)
DEESSER['tr'] = LinearFloatSliderAndSpinBox('tr', 5000, 1, 20)

VBASS = OrderedDict()
VBASS['onoff'] = Switch('onoff', 'on')
VBASS['fcReson'] = LogIntSliderAndSpinBox('fcReson', 500, 40, 100)
VBASS['fcLBPF'] = LogIntSliderAndSpinBox('fcLBPF', 500, 40, 400)
VBASS['LPGain'] = LinearFloatSliderAndSpinBox('LPGain', 12, -80, 0)
VBASS['VBGain'] = LinearFloatSliderAndSpinBox('VBGain', 12, -80, 0)
VBASS['HPGain'] = LinearFloatSliderAndSpinBox('HPGain', 12, -80, 0)
VBASS['intens'] = LinearIntSliderAndSpinBox('intens', 9, 1, 5)

AGC = OrderedDict()
AGC['onoff'] = Switch('onoff', 'on')
AGC['linear gain'] = LinearFloatSliderAndSpinBox('linear gain', 50, 0, 8,
                                                 additional_parameters={'pRowWidth': [70, 90, 50, 100]})
AGC['target'] = LinearFloatSliderAndSpinBox('target', 0, -24, -8,
                                            additional_parameters={'pRowWidth': [70, 90, 50, 100]})
AGC['ratio'] = LinearFloatSliderAndSpinBox('ratio', 24, 1, 3,
                                           additional_parameters={'pRowWidth': [70, 90, 50, 100]})
AGC['loThres'] = LinearFloatSliderAndSpinBox('loThres', -30, -120, -60,
                                           additional_parameters={'pRowWidth': [70, 90, 50, 100]})

SRC = OrderedDict()
SRC['srin'] = DisableMenu('Input_Freq', ['8000','16000', '32000', '44100', '48000', '88200', '96000', '176400', '192000'], '44100')
SRC['srout'] = DisableMenu('Output_Freq', ['8000','16000', '32000', '44100', '48000', '88200', '96000', '176400', '192000'], '44100')
SRC['Quality'] = DisableMenu('Quality', ['Best', 'Medium', 'Fastest'], 'Fastest')
# SRC['Latency'] = LabelValue('Latency', 1)


DBASS = OrderedDict()
DBASS['onoff'] = Switch('onoff', 'on')
DBASS['HiThres'] = LinearFloatSliderAndSpinBox('HiThres', 0, -30, -10)
DBASS['LoThres'] = LinearFloatSliderAndSpinBox('LoThres', -30, -70, -60)
DBASS['fc'] = LogIntSliderAndSpinBox('fc', 350, 20, 122)
DBASS['ratio'] = LinearFloatSliderAndSpinBox('ratio', 1.2, 0.2, 1)

DBASS_FP = OrderedDict()
DBASS_FP['onoff'] = Switch('onoff', 'on')
DBASS_FP['HiThres'] = LinearFloatSliderAndSpinBox('HiThres', 0, -30, -10)
DBASS_FP['LoThres'] = LinearFloatSliderAndSpinBox('LoThres', -30, -70, -60)
DBASS_FP['fc'] = LogIntSliderAndSpinBox('fc', 350, 20, 122)
DBASS_FP['ratio'] = LinearFloatSliderAndSpinBox('ratio', 1.2, 0.2, 1)

DLOUDNESS = OrderedDict()
DLOUDNESS['onoff'] = Switch('onoff', 'on')
DLOUDNESS['HiThres'] = LinearFloatSliderAndSpinBox('HiThres', 0, -30, -10)
DLOUDNESS['LoThres'] = LinearFloatSliderAndSpinBox('LoThres', -30, -70, -60)
DLOUDNESS['ratio'] = LinearFloatSliderAndSpinBox('ratio', 1.2, 0.2, 1)

DYNAMIC_EQ = OrderedDict()
DYNAMIC_EQ['onoff'] = Switch('onoff', 'on')
DYNAMIC_EQ['inputGain'] = LinearFloatSliderAndSpinBox('inputGain', 0.0, -40.0, 0.0)
DYNAMIC_EQ['maxDBFS'] = LinearFloatSliderAndSpinBox('maxDBFS', 0.0, -20.0, 0.0)
DYNAMIC_EQ['ratio'] = LinearFloatSliderAndSpinBox('ratio', 1.2, 0.2, 1.0)
DYNAMIC_EQ['LoudnessCurve'] = Menu('LoudnessCurve', ['SOFT', 'HARD'], 'SOFT')
# DYNAMIC_EQ['HiThres'] = LinearFloatSliderAndSpinBox('HiThres', -10.0, -30.0, -10.0)
# DYNAMIC_EQ['LimitThres'] = LinearFloatSliderAndSpinBox('LimitThres', -10.0, -40.0, -10.0)
DYNAMIC_EQ['Equalizer'] = Menu('Equalizer', ['Default', 'Music', 'Movie', 'Game'], 'Default')


SPATIALIZER = OrderedDict()
SPATIALIZER['onoff'] = Switch('onoff', 'on')
SPATIALIZER['DepthH'] = LinearFloatSliderAndSpinBox('Depth_H', 30, -30, 0)
SPATIALIZER['DepthM'] = LinearFloatSliderAndSpinBox('Depth_M', 30, -30, 0)
SPATIALIZER['DepthL'] = LinearFloatSliderAndSpinBox('Depth_L', 30, -30, 0)
SPATIALIZER['Blend'] = LinearFloatSliderAndSpinBox('Blend', 0, -120, 0)

SMART_EQ = OrderedDict()
SMART_EQ['onoff'] = Switch('onoff', 'on', additional_parameters={'pRowWidth': [90, 90, 50, 140]})
SMART_EQ['fc'] = LinearFloatSliderAndSpinBox('fc', 22000, 20, 200,
                                             additional_parameters={'pRowWidth': [90, 90, 50, 140]})
SMART_EQ['fsboost'] = LinearFloatSliderAndSpinBox('fsboost', 24.0, -24.0, 0,
                                                  additional_parameters={'pRowWidth': [90, 90, 50, 140]})
SMART_EQ['minboost'] = LinearFloatSliderAndSpinBox('minboost (dB)', 0.0, -15.0, -15.0,
                                                   additional_parameters={'pRowWidth': [90, 90, 50, 140]})
SMART_EQ['maxboost'] = LinearFloatSliderAndSpinBox('maxboost (dB)', 15.0, 0.0, 15.0,
                                                   additional_parameters={'pRowWidth': [90, 90, 50, 140]})
SMART_EQ['slope'] = LinearFloatSliderAndSpinBox('slope', 1.8, 0.1, 0.707)
SMART_EQ['effthold'] = LinearFloatSliderAndSpinBox('effthold', 1.0, 0, 0.0001)
SMART_EQ['ta'] = LinearFloatSliderAndSpinBox('ta', 1000000, 0, 2266.8)
SMART_EQ['tr'] = LinearFloatSliderAndSpinBox('tr', 1000000, 0.1, 2266.8)
SMART_EQ['tf'] = LinearFloatSliderAndSpinBox('tf', 1000000, 0.1, 2266.8)

AFS = OrderedDict()
AFS['onoff'] = Switch('onoff', 'on')
AFS['absthres'] = LinearIntSliderAndSpinBox('absthres', 0, -90, -66)
AFS['ballK'] = LinearIntSliderAndSpinBox('ballK', 500, 10, 100)

######################  VOICE  ######################

BEAMFORMING = OrderedDict()
BEAMFORMING['onoff'] = Switch('onoff', 'on')
BEAMFORMING['DOA'] = Switch('DOA', 'off')
BEAMFORMING['MicDeg'] = LinearIntSliderAndSpinBox('MicDeg', 360, 0, 30)
BEAMFORMING['Mic1X'] = LinearFloatSliderAndSpinBox('Mic1X', 100, -100, 0)
BEAMFORMING['Mic1Y'] = LinearFloatSliderAndSpinBox('Mic1Y', 100, -100, 0)
BEAMFORMING['Mic2X'] = LinearFloatSliderAndSpinBox('Mic2X', 100, -100, 0)
BEAMFORMING['Mic2Y'] = LinearFloatSliderAndSpinBox('Mic2Y', 100, -100, 0)
BEAMFORMING['Mic3X'] = LinearFloatSliderAndSpinBox('Mic3X', 100, -100, 0)
BEAMFORMING['Mic3Y'] = LinearFloatSliderAndSpinBox('Mic3Y', 100, -100, 0)
BEAMFORMING['Mic4X'] = LinearFloatSliderAndSpinBox('Mic4X', 100, -100, 0)
BEAMFORMING['Mic4Y'] = LinearFloatSliderAndSpinBox('Mic4Y', 100, -100, 0)

BEAMFORMING_3ch = OrderedDict()
BEAMFORMING_3ch['onoff'] = Switch('onoff', 'on')
BEAMFORMING_3ch['DOA'] = Switch('DOA', 'off')
BEAMFORMING_3ch['MicDeg'] = LinearIntSliderAndSpinBox('MicDeg', 360, 0, 30)
BEAMFORMING_3ch['Mic1X'] = LinearFloatSliderAndSpinBox('Mic1X', 100, -100, 0)
BEAMFORMING_3ch['Mic1Y'] = LinearFloatSliderAndSpinBox('Mic1Y', 100, -100, 0)
BEAMFORMING_3ch['Mic2X'] = LinearFloatSliderAndSpinBox('Mic2X', 100, -100, 0)
BEAMFORMING_3ch['Mic2Y'] = LinearFloatSliderAndSpinBox('Mic2Y', 100, -100, 0)
BEAMFORMING_3ch['Mic3X'] = LinearFloatSliderAndSpinBox('Mic3X', 100, -100, 0)
BEAMFORMING_3ch['Mic3Y'] = LinearFloatSliderAndSpinBox('Mic3Y', 100, -100, 0)
BEAMFORMING_3ch['Mic4X'] = LinearFloatSliderAndSpinBox('Mic4X', 100, -100, 0)
BEAMFORMING_3ch['Mic4Y'] = LinearFloatSliderAndSpinBox('Mic4Y', 100, -100, 0)

BEAMFORMING_2ch = OrderedDict()
BEAMFORMING_2ch['onoff'] = Switch('onoff', 'on')
BEAMFORMING_2ch['DOA'] = Switch('DOA', 'off')
BEAMFORMING_2ch['MicDeg'] = LinearIntSliderAndSpinBox('MicDeg', 360, 0, 30)
BEAMFORMING_2ch['Mic1X'] = LinearFloatSliderAndSpinBox('Mic1X', 100, -100, 0)
BEAMFORMING_2ch['Mic1Y'] = LinearFloatSliderAndSpinBox('Mic1Y', 100, -100, 0)
BEAMFORMING_2ch['Mic2X'] = LinearFloatSliderAndSpinBox('Mic2X', 100, -100, 0)
BEAMFORMING_2ch['Mic2Y'] = LinearFloatSliderAndSpinBox('Mic2Y', 100, -100, 0)
BEAMFORMING_2ch['Mic3X'] = LinearFloatSliderAndSpinBox('Mic3X', 100, -100, 0)
BEAMFORMING_2ch['Mic3Y'] = LinearFloatSliderAndSpinBox('Mic3Y', 100, -100, 0)
BEAMFORMING_2ch['Mic4X'] = LinearFloatSliderAndSpinBox('Mic4X', 100, -100, 0)
BEAMFORMING_2ch['Mic4Y'] = LinearFloatSliderAndSpinBox('Mic4Y', 100, -100, 0)

VEP = OrderedDict()
VEP['onoff'] = Switch('onoff', 'on')
VEP['DOA'] = Switch('DOA', 'off')
VEP['MicDeg'] = LinearIntSliderAndSpinBox('MicDeg', 360, 0, 30)
VEP['Mic1X'] = LinearFloatSliderAndSpinBox('Mic1X', 100, -100, 0)
VEP['Mic1Y'] = LinearFloatSliderAndSpinBox('Mic1Y', 100, -100, 0)
VEP['Mic2X'] = LinearFloatSliderAndSpinBox('Mic2X', 100, -100, 0)
VEP['Mic2Y'] = LinearFloatSliderAndSpinBox('Mic2Y', 100, -100, 0)
VEP['Mic3X'] = LinearFloatSliderAndSpinBox('Mic3X', 100, -100, 0)
VEP['Mic3Y'] = LinearFloatSliderAndSpinBox('Mic3Y', 100, -100, 0)
VEP['Mic4X'] = LinearFloatSliderAndSpinBox('Mic4X', 100, -100, 0)
VEP['Mic4Y'] = LinearFloatSliderAndSpinBox('Mic4Y', 100, -100, 0)

PHASEVOCODER = OrderedDict()
PHASEVOCODER['onoff'] = Switch('onoff', 'on')
PHASEVOCODER['pitchType'] = Menu('pitchType',
                          ['Male', 'Female', 'Monster', 'Cartoon'], 'Male')

COHBF = OrderedDict()
COHBF['onoff'] = Switch('onoff', 'on')

AEC = OrderedDict()
AEC['onoff'] = Switch('onoff', 'on')
AEC['filterLen'] = LinearFloatSliderAndSpinBox('filterLen', 300, 64, 120)

NOISEREDUCTION = OrderedDict()
NOISEREDUCTION['onoff'] = Switch('onoff', 'on')
NOISEREDUCTION['strength'] = LinearFloatSliderAndSpinBox('strength', 1, 0, 0.5)

CLIPFIX = OrderedDict()
CLIPFIX['onoff'] = Switch('onoff', 'on')
CLIPFIX['difGain'] = LinearFloatSliderAndSpinBox('difGain', 24, 0, 20)
CLIPFIX['target'] = LinearFloatSliderAndSpinBox('target', 0, -24, -4)
CLIPFIX['ta'] = LinearFloatSliderAndSpinBox('ta', 2000, 0.1, 0.1)
CLIPFIX['tr'] = LinearFloatSliderAndSpinBox('tr', 5000, 1, 1)
CLIPFIX['taS'] = LinearFloatSliderAndSpinBox('taS', 2000, 0.1, 0.1)
CLIPFIX['trS'] = LinearFloatSliderAndSpinBox('trS', 5000, 1, 1)
CLIPFIX['factory'] = Menu('factory', ['off', 'channel1', 'channel0'], 'off')
CLIPFIX['gain'] = LinearFloatSliderAndSpinBox('gain', 40, -90, 0)

#########################  MISCS  #########################

METER = OrderedDict()

METER_FP = OrderedDict()

IR = OrderedDict()
IR['onoff'] = Switch('onoff', 'on')
IR['gain'] = LinearFloatSliderAndSpinBox('gain', 24, -120, 0)
IR['path'] = FileLoader('path', [{'Waveform Audio File': ['wav']}])

# IR_ST = OrderedDict()
# IR_ST['onoff'] = Switch('onoff', 'on')
# IR_ST['gain'] = LinearFloatSliderAndSpinBox('gain', 24, -120, 0)
# IR_ST['path'] = FileLoader('path', [{'Waveform Audio File': ['wav']}])

SPECTRUM = OrderedDict()
SPECTRUM['fftsize'] = Menu('fftsize', ['128', '256', '512', '1024', '2048', '4096', '8192', '16384'], '1024')
SPECTRUM['window'] = Menu('window', ['None', 'Rectangular', 'Hann', 'Blackmann-Harris', 'Hamming'], 'Hann')

CROSSFEED = OrderedDict()
CROSSFEED['fftsize'] = Menu('fftsize', ['512', '1024'], '512')
# CROSSFEED['window'] = Menu('window', ['None', 'Rectangular', 'Hann', 'Blackmann-Harris', 'Hamming'], 'Hann')
CROSSFEED['onoff'] = Switch('onoff', 'on')
# CROSSFEED['ITD'] = Switch('ITD', 'on')
CROSSFEED['angle'] = LinearIntSliderAndSpinBox('angle', 90, 0, 45)
CROSSFEED['distance'] = LinearIntSliderAndSpinBox('distance', 200, 25, 25)
CROSSFEED['head'] = LinearIntSliderAndSpinBox('head', 20, 10, 15)

CTC = OrderedDict()
CTC['onoff'] = Switch('onoff', 'on')
CTC['fcLF'] = LogIntSliderAndSpinBox('fcLF', 20000, 20, 200, additional_parameters={'pRowWidth': [70, 90, 50, 100]})
CTC['fcHF'] = LogIntSliderAndSpinBox('fcHF', 20000, 20, 4000, additional_parameters={'pRowWidth': [70, 90, 50, 100]})
CTC['attenuate'] = LinearFloatSliderAndSpinBox('attenuate', 0, -5, -2.5, additional_parameters={'pRowWidth': [70, 90, 50, 100]})
CTC['delay'] =  LinearFloatSliderAndSpinBox('delay', 0.2, 0, 0.06, additional_parameters={'pRowWidth': [70, 90, 50, 100]})
CTC['lowGain'] = LinearFloatSliderAndSpinBox('lowGain', 0, -15, 0, additional_parameters={'pRowWidth': [70, 90, 50, 100]})
CTC['bandGain'] = LinearFloatSliderAndSpinBox('bandGain', 0, -15, 0, additional_parameters={'pRowWidth': [70, 90, 50, 100]})
CTC['highGain'] = LinearFloatSliderAndSpinBox('highGain', 0, -15, 0, additional_parameters={'pRowWidth': [70, 90, 50, 100]})

DLFQ = OrderedDict()
DLFQ['onoff'] = Switch('onoff', 'on')
DLFQ['intensity'] = LinearIntSliderAndSpinBox('intensity', 10, 0, 5)
DLFQ['band'] = LinearIntSliderAndSpinBox('band', 400, 100, 200, additional_parameters={'pStep': 50})

AI_NR = OrderedDict()
AI_NR['onoff'] = Switch('onoff', 'on')

AI_NR_UC = OrderedDict()
AI_NR_UC['onoff'] = Switch('onoff', 'on')

AI_NR_48K = OrderedDict()
AI_NR_48K['onoff'] = Switch('onoff', 'on')

# AI_BF = OrderedDict()
# AI_BF['onoff'] = Switch('onoff', 'on')

COMMENT = OrderedDict()

SUBPATCH = OrderedDict()

RTA = OrderedDict()

BPM = OrderedDict()

#########################  3rd party  #########################
NTTS_IML = OrderedDict()
NTTS_IML['onoff'] = Switch('onoff', 'on', additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['BfPwcUp'] = LinearFloatSliderAndSpinBox('BfPwcUp', 20, 4, 12,
                                                  additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['BfPwcDn'] = LinearFloatSliderAndSpinBox('BfPwcDn', 20, 4, 12,
                                                  additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Att0to250'] = LinearFloatSliderAndSpinBox('Att0to250', 0, -40, -10,
                                                    additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Att250to500'] = LinearFloatSliderAndSpinBox('Att250to500', 0, -40, -10,
                                                      additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Att500o1k'] = LinearFloatSliderAndSpinBox('Att500o1k', 0, -40, -10,
                                                    additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Att1kto2k'] = LinearFloatSliderAndSpinBox('Att1kto2k', 0, -40, -10,
                                                    additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Att2kto4k'] = LinearFloatSliderAndSpinBox('Att2kto4k', 0, -40, -10,
                                                    additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Att4kto8k'] = LinearFloatSliderAndSpinBox('Att4kto8k', 0, -40, -10,
                                                    additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['BfAtt0to8k'] = LinearFloatSliderAndSpinBox('BfAtt0to8k', 0, -40, -20,
                                                     additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['EchoAtt0to8k'] = LinearFloatSliderAndSpinBox('EchoAtt0to8k', 0, -40, -40,
                                                       additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Thr0to250'] = LinearFloatSliderAndSpinBox('Thr0to250', 4, 0, 2.5,
                                                    additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Thr250to500'] = LinearFloatSliderAndSpinBox('Thr250to500', 4, 0, 1.5,
                                                      additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Thr500to1k'] = LinearFloatSliderAndSpinBox('Thr500to1k', 4, 0, 1.5,
                                                     additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Thr1kto2k'] = LinearFloatSliderAndSpinBox('Thr1kto2k', 4, 0, 1.5,
                                                    additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Thr2kto4k'] = LinearFloatSliderAndSpinBox('Thr2kto4k', 4, 0, 1.3,
                                                    additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['Thr4kto8k'] = LinearFloatSliderAndSpinBox('Thr4kto8k', 4, 0, 1.3,
                                                    additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['ThrV'] = LinearFloatSliderAndSpinBox('ThrV', 4, 0, 1.0,
                                               additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['ThrN'] = LinearFloatSliderAndSpinBox('ThrN', 4, 0, 2.0,
                                               additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['BfThrV'] = LinearFloatSliderAndSpinBox('BfThrV', 4, 0, 1.0,
                                                 additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['BfThrN'] = LinearFloatSliderAndSpinBox('BfThrN', 4, 0, 1.0,
                                                 additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['EchoMgnRcv'] = LinearFloatSliderAndSpinBox('EchoMgnRcv', 20, -20, 9.0,
                                                     additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['EchoMgnSnd'] = LinearFloatSliderAndSpinBox('EchoMgnSnd', 20, -20, -6.0,
                                                     additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['EchoMgnLarge'] = LinearFloatSliderAndSpinBox('EchoMgnLarge', 20, -20, 9.0,
                                                       additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['gPwc0to250'] = LinearFloatSliderAndSpinBox('gPwc0to250', 40, 4, 40.0,
                                                     additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['gPwc250to500'] = LinearFloatSliderAndSpinBox('gPwc250to500', 40, 4, 30.0,
                                                       additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['gPwc500to1k'] = LinearFloatSliderAndSpinBox('gPwc500to1k', 40, 4, 25.0,
                                                      additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['gPwc1kto2k'] = LinearFloatSliderAndSpinBox('gPwc1kto2k', 40, 4, 10.0,
                                                     additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['gPwc2kto4k'] = LinearFloatSliderAndSpinBox('gPwc2kto4k', 40, 4, 15.0,
                                                     additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['gPwc4kto8k'] = LinearFloatSliderAndSpinBox('gPwc4kto8k', 40, 4, 15.0,
                                                     additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_IML['ngen1v1'] = LinearFloatSliderAndSpinBox('ngen1v1', 6, -99, 0.0,
                                                  additional_parameters={'pRowWidth': [100, 90, 50, 140]})

NTTS_AGC = OrderedDict()
NTTS_AGC['onoff'] = Switch('onoff', 'on',
                           additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['BypassAGC'] = Switch('BypassAGC', 'off',
                               additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['PwrPwcUpTime'] = LinearFloatSliderAndSpinBox('PwrPwcUpTime', 300, 4, 50, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['PwrPwcDnTime'] = LinearFloatSliderAndSpinBox('PwrPwcDnTime', 300, 4, 50, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp1'] = LinearFloatSliderAndSpinBox('THTabUp1', 0, -80, -60, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp2'] = LinearFloatSliderAndSpinBox('THTabUp2', 0, -80, -58, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp3'] = LinearFloatSliderAndSpinBox('THTabUp3', 0, -80, -56, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp4'] = LinearFloatSliderAndSpinBox('THTabUp4', 0, -80, -54, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp5'] = LinearFloatSliderAndSpinBox('THTabUp5', 0, -80, -52, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp6'] = LinearFloatSliderAndSpinBox('THTabUp6', 0, -80, -50, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp7'] = LinearFloatSliderAndSpinBox('THTabUp7', 0, -80, -48, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp8'] = LinearFloatSliderAndSpinBox('THTabUp8', 0, -80, -46, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp9'] = LinearFloatSliderAndSpinBox('THTabUp9', 0, -80, -44, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabUp10'] = LinearFloatSliderAndSpinBox('THTabUp10', 0, -80, -42, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn1'] = LinearFloatSliderAndSpinBox('THTabDn1', 0, -80, -62, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn2'] = LinearFloatSliderAndSpinBox('THTabDn2', 0, -80, -60, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn3'] = LinearFloatSliderAndSpinBox('THTabDn3', 0, -80, -58, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn4'] = LinearFloatSliderAndSpinBox('THTabDn4', 0, -80, -56, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn5'] = LinearFloatSliderAndSpinBox('THTabDn5', 0, -80, -54, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn6'] = LinearFloatSliderAndSpinBox('THTabDn6', 0, -80, -52, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn7'] = LinearFloatSliderAndSpinBox('THTabDn7', 0, -80, -50, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn8'] = LinearFloatSliderAndSpinBox('THTabDn8', 0, -80, -48, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn9'] = LinearFloatSliderAndSpinBox('THTabDn9', 0, -80, -46, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['THTabDn10'] = LinearFloatSliderAndSpinBox('THTabDn10', 0, -80, -44, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab1'] = LinearFloatSliderAndSpinBox('GnTab1', 10, -40, -20, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab2'] = LinearFloatSliderAndSpinBox('GnTab2', 10, -40, -18, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab3'] = LinearFloatSliderAndSpinBox('GnTab3', 10, -40, -16, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab4'] = LinearFloatSliderAndSpinBox('GnTab4', 10, -40, -14, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab5'] = LinearFloatSliderAndSpinBox('GnTab5', 10, -40, -12, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab6'] = LinearFloatSliderAndSpinBox('GnTab6', 10, -40, -10, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab7'] = LinearFloatSliderAndSpinBox('GnTab7', 10, -40, -8, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab8'] = LinearFloatSliderAndSpinBox('GnTab8', 10, -40, -6, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab9'] = LinearFloatSliderAndSpinBox('GnTab9', 10, -40, -4, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab10'] = LinearFloatSliderAndSpinBox('GnTab10', 10, -40, -2, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['GnTab11'] = LinearFloatSliderAndSpinBox('GnTab11', 10, -40, 0, additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['NLPwcUpTime'] = LinearFloatSliderAndSpinBox('NLPwcUpTime', 1000.0, 20, 500.0,
                                                      additional_parameters={'pRowWidth': [100, 90, 50, 140]})
NTTS_AGC['NLPwcDnTime'] = LinearFloatSliderAndSpinBox('NLPwcDnTime', 1000.0, 20, 500.0,
                                                      additional_parameters={'pRowWidth': [100, 90, 50, 140]})

UPHEAR_VIRT = OrderedDict()
UPHEAR_VIRT['SBBSDir'] = FileLoader('SBBSDir', None, {'pRowWidth': [90, 90, 50, 140]})
UPHEAR_VIRT['SoundMode'] = Menu('SoundMode', ['Off', 'Regular'], 'Regular',
                                additional_parameters={'pRowWidth': [90, 90, 50, 140]})
UPHEAR_VIRT['Dynamic Bass'] = Switch('Dynamic Bass', 'on',
                                     additional_parameters={'pRowWidth': [90, 90, 50, 140]})
UPHEAR_VIRT['Excursion Limiter'] = Switch('Excursion Limiter', 'off',
                                          additional_parameters={'pRowWidth': [90, 90, 50, 140]})
UPHEAR_VIRT['MasterVol'] = LinearIntSliderAndSpinBox('MasterVol', 10, -80, 0,
                                                     additional_parameters={'pRowWidth': [90, 90, 50, 140]})
UPHEAR_VIRT['UserEQ (band 1)'] = LinearFloatSliderAndSpinBox('UserEQ (band 1)', 9.5, -9.5, 0,
                                                             additional_parameters={'pRowWidth': [90, 90, 50, 140]})
UPHEAR_VIRT['UserEQ (band 2)'] = LinearFloatSliderAndSpinBox('UserEQ (band 2)', 9.5, -9.5, 0,
                                                             additional_parameters={'pRowWidth': [90, 90, 50, 140]})
UPHEAR_VIRT['UserEQ (band 3)'] = LinearFloatSliderAndSpinBox('UserEQ (band 3)', 9.5, -9.5, 0,
                                                             additional_parameters={'pRowWidth': [90, 90, 50, 140]})
UPHEAR_VIRT['UserEQ (band 4)'] = LinearFloatSliderAndSpinBox('UserEQ (band 4)', 9.5, -9.5, 0,
                                                             additional_parameters={'pRowWidth': [90, 90, 50, 140]})

upHear_VQE = OrderedDict()
upHear_VQE['onoff'] = Switch('onoff', 'on')
upHear_VQE['UrocMicSetup'] = Menu('UrocMicSetup', ['INVALID', 'SINGLE', 'DUAL',
                                                   'QUAD_ULA', 'QUAD_NONULA', 'OCTA_ULA',
                                                   '6_ULA', '3_ULA', 'OCTA_CIRC_UNIFORM',
                                                   '6_PLUS_1_CIRC', 'QUAD_CIRC_UNIFORM',
                                                   '3_PLUS_1_CIRC', '6_CIRC_UNIFORM', '3_CIRC_UNIFORM',
                                                   '5_CIRC_UNIFORM', 'CUSTOM_EL1_8M_2D'],
                                  'INVALID',
                                  additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['MicDist1'] = LinearFloatSliderAndSpinBox('MicDist1', 100, 0, 7,
                                                     additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['MicDist2'] = LinearFloatSliderAndSpinBox('MicDist2', 100, 0, 0,
                                                     additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['FrameSize'] = Menu('FrameSize', ['256', '512', '1024'], '512',
                               additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['FilterLength'] = LinearIntSliderAndSpinBox('FilterLength', 1000, 0, 100,
                                                       additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['delaymode'] = Menu('delaymode', ['MODE_INVALID', 'MODE_FIXED', 'MODE_ADAPTIVE'], 'MODE_ADAPTIVE',
                               additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['Delay'] = LinearIntSliderAndSpinBox('Delay', 2000, 150, 300,
                                                additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['processmode'] = Menu('processmode', ['MODE_INVALID', 'MODE_COM', 'MODE_ASR'], 'MODE_COM',
                                 additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['natt'] = LinearFloatSliderAndSpinBox('natt', 0, -100, -15,
                                                 additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['pal'] = LinearFloatSliderAndSpinBox('pal', 0, -150, -100,
                                                 additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['agc'] = LinearFloatSliderAndSpinBox('agc', 30, -30, 0,
                                                additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['numSpk'] = LinearIntSliderAndSpinBox('numSpk', 8, 0, 1,
                                                 additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['id'] = Menu('id', ['10021','10022','10023','10024', '10025'], '10023',
                        additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['beam'] = LinearIntSliderAndSpinBox('beam', 2, 0, 0,
                                               additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['BeamDir'] = LinearFloatSliderAndSpinBox('BeamDir', 180, -180, 0,
                                                    additional_parameters={'pRowWidth': [80, 90, 50, 140]})
upHear_VQE['profile'] = LinearIntSliderAndSpinBox('profile', 50, 0, 0,
                                                    additional_parameters={'pRowWidth': [80, 90, 50, 140]})

AI_ZIP = OrderedDict()
AI_ZIP['vocalremove'] = LinearFloatSliderAndSpinBox('Vocal Level', 0, -200, -10,
                                                    additional_parameters={'pRowWidth': [70, 90, 50, 140]})

AI_ZIP_DE = OrderedDict()
AI_ZIP_DE['onoff'] = Switch('onoff', 'on')
AI_ZIP_DE['vocalgain'] = LinearFloatSliderAndSpinBox('Vocal Level', 15, 1, 6,
                                                    additional_parameters={'pRowWidth': [70, 90, 50, 140]})

BD_SOUND = OrderedDict()
BD_SOUND['onoff'] = Switch('BdSound_Enable', 'on')
BD_SOUND['MicOnoff'] = Switch('mic_onoff', 'on')
BD_SOUND['EQonoff'] = Switch('EQ_Enable', 'on')
BD_SOUND['MicPreGain'] = LinearFloatSliderAndSpinBox('mic_pre_gain', 24, 0, 10)
BD_SOUND['MicPostGain'] = LinearFloatSliderAndSpinBox('mic_post_gain', 20, -20, 0)
BD_SOUND['MicDelayOffset'] = LogIntSliderAndSpinBox('mic_delay_offset', 20, 1, 1)
BD_SOUND['NoiseLevel'] = LinearFloatSliderAndSpinBox('Noise_Lvl', 0, -100, -100)

#########################  Wrapping Child Dict Into Parent Dict  #########################

AUDIO_OBJECT = OrderedDict()

AUDIO_OBJECT['IN'] = IN
AUDIO_OBJECT['INLET'] = INLET
AUDIO_OBJECT['OUT'] = OUT
AUDIO_OBJECT['OUTLET'] = OUTLET
AUDIO_OBJECT['WAVPLAYER'] = WAVPLAYER
AUDIO_OBJECT['TONEGEN'] = TONEGEN
AUDIO_OBJECT['NOISEGEN'] = NOISEGEN
AUDIO_OBJECT['CHIRP'] = CHIRP
AUDIO_OBJECT['VISUALIZER'] = VISUALIZER
AUDIO_OBJECT['DUMP'] = DUMP
AUDIO_OBJECT['FEEDBACK'] = FEEDBACK
AUDIO_OBJECT['Xpatial'] = XPATIAL
AUDIO_OBJECT['DLFQ'] = DLFQ

AUDIO_OBJECT['ADDER'] = ADDER
AUDIO_OBJECT['NEGATOR'] = NEGATOR
AUDIO_OBJECT['ABS'] = ABS
AUDIO_OBJECT['SQRT'] = SQRT
AUDIO_OBJECT['RMS'] = RMS
AUDIO_OBJECT['MOVAV'] = MOVAV
AUDIO_OBJECT['MULTIPLIER'] = MULTIPLIER
AUDIO_OBJECT['SUBTRACTOR'] = SUBTRACTOR

AUDIO_OBJECT['BIQUAD'] = BIQUAD
AUDIO_OBJECT['BIQUAD_LOAD'] = BIQUAD_LOAD
AUDIO_OBJECT['PEQ'] = PEQ
AUDIO_OBJECT['PEQ_V2'] = PEQ_V2
AUDIO_OBJECT['LPF'] = LPF
AUDIO_OBJECT['HPF'] = HPF
AUDIO_OBJECT['XOVER'] = XOVER
AUDIO_OBJECT['IIRCOEF'] = IIRCOEF
AUDIO_OBJECT['FIR'] = FIR
AUDIO_OBJECT['FIR_LOAD'] = FIR_LOAD
AUDIO_OBJECT['GAME_EQ'] = GAME_EQ
AUDIO_OBJECT['Custom_EQ'] = CustomEQ
AUDIO_OBJECT['LMS'] = LMS

AUDIO_OBJECT['GAIN'] = GAIN
AUDIO_OBJECT['GAIN_ST'] = GAIN_ST
AUDIO_OBJECT['SMART_GAIN'] = SMART_GAIN
AUDIO_OBJECT['ATTEN'] = ATTEN
AUDIO_OBJECT['ATTEN_ST'] = ATTEN_ST
AUDIO_OBJECT['MUTE'] = MUTE
AUDIO_OBJECT['LOUDNESS'] = LOUDNESS
AUDIO_OBJECT['POLARITY'] = POLARITY
AUDIO_OBJECT['QUICK_GAIN'] = QUICK_GAIN

AUDIO_OBJECT['LIMITER'] = LIMITER
AUDIO_OBJECT['LIMITER_MB'] = LIMITER_MB
AUDIO_OBJECT['COMP'] = COMP
AUDIO_OBJECT['COMP_Combo'] = COMP_Combo
AUDIO_OBJECT['AUTO_COMP'] = AUTO_COMP
AUDIO_OBJECT['CLIPPER'] = CLIPPER
AUDIO_OBJECT['GATE'] = GATE
AUDIO_OBJECT['SMART_GATE'] = SMART_GATE
AUDIO_OBJECT['DYNAMIC_FILTER'] = DYNAMIC_FILTER
AUDIO_OBJECT['DYNAMIC_EQ'] = DYNAMIC_EQ
AUDIO_OBJECT['AGC'] = AGC
AUDIO_OBJECT['SRC'] = SRC

AUDIO_OBJECT['MERGER'] = MERGER
AUDIO_OBJECT['MIXER8'] = MIXER8
AUDIO_OBJECT['MIXER'] = MIXER
AUDIO_OBJECT['MUX'] = MUX
AUDIO_OBJECT['MUX_ST'] = MUX_ST
AUDIO_OBJECT['DRYWET'] = DRYWET

AUDIO_OBJECT['DELAY'] = DELAY
AUDIO_OBJECT['DELAY_Intp'] = DELAY_Intp
AUDIO_OBJECT['MULTITAP'] = MULTITAP
AUDIO_OBJECT['LONG_APF'] = LONG_APF
AUDIO_OBJECT['LPF_COMB_FILTER'] = LPF_COMB_FILTER
# AUDIO_OBJECT['REVERB'] = REVERB
AUDIO_OBJECT['REVERB_V2'] = REVERB_V2
AUDIO_OBJECT['CHORUS'] = CHORUS
AUDIO_OBJECT["DIRAC"] = DIRAC

AUDIO_OBJECT['METER'] = METER
AUDIO_OBJECT['IR'] = IR
# AUDIO_OBJECT['IR_ST'] = IR_ST
AUDIO_OBJECT['SPECTRUM'] = SPECTRUM
AUDIO_OBJECT['CROSSFEED'] = CROSSFEED
AUDIO_OBJECT['RTA'] = RTA
AUDIO_OBJECT['BPM'] = BPM
AUDIO_OBJECT['ROOM_FIX'] = ROOM_FIX
AUDIO_OBJECT['COMMENT'] = COMMENT
AUDIO_OBJECT['SUBPATCH'] = SUBPATCH
AUDIO_OBJECT['VAD'] = VAD

AUDIO_OBJECT['VAD_IABSE'] = VAD_IABSE
AUDIO_OBJECT['DEESSER'] = DEESSER
AUDIO_OBJECT['VBASS'] = VBASS
AUDIO_OBJECT['DBASS'] = DBASS
AUDIO_OBJECT['DLOUDNESS'] = DLOUDNESS
AUDIO_OBJECT['DYNAMIC_EQ'] = DYNAMIC_EQ

AUDIO_OBJECT['AEC'] = AEC
AUDIO_OBJECT['BEAMFORMING'] = BEAMFORMING
AUDIO_OBJECT['AI_NR'] = AI_NR
# AUDIO_OBJECT['AI_BF'] = AI_BF
AUDIO_OBJECT['BEAMFORMING_2ch'] = BEAMFORMING_2ch
AUDIO_OBJECT['BEAMFORMING_3ch'] = BEAMFORMING_3ch
AUDIO_OBJECT['VEP'] = VEP
AUDIO_OBJECT['COHBF'] = COHBF

AUDIO_OBJECT['VAD_IABSE'] = VAD_IABSE
AUDIO_OBJECT['DEESSER'] = DEESSER
AUDIO_OBJECT['VBASS'] = VBASS
AUDIO_OBJECT['DBASS'] = DBASS
AUDIO_OBJECT['DLOUDNESS'] = DLOUDNESS
AUDIO_OBJECT['AEC'] = AEC
AUDIO_OBJECT['BEAMFORMING'] = BEAMFORMING
AUDIO_OBJECT['AI_NR'] = AI_NR
AUDIO_OBJECT['AI_NR_UC'] = AI_NR_UC
AUDIO_OBJECT['AI_NR_48K'] = AI_NR_48K
# AUDIO_OBJECT['AI_BF'] = AI_BF
AUDIO_OBJECT['BEAMFORMING_2ch'] = BEAMFORMING_2ch
AUDIO_OBJECT['BEAMFORMING_3ch'] = BEAMFORMING_3ch
AUDIO_OBJECT['VEP'] = VEP
AUDIO_OBJECT['PHASEVOCODER'] = PHASEVOCODER

AUDIO_OBJECT['NOISEREDUCTION'] = NOISEREDUCTION
AUDIO_OBJECT['CLIPFIX'] = CLIPFIX
AUDIO_OBJECT['SPATIALIZER'] = SPATIALIZER
AUDIO_OBJECT['SMART_EQ'] = SMART_EQ
AUDIO_OBJECT['CTC'] = CTC
AUDIO_OBJECT['AFS'] = AFS


AUDIO_OBJECT['NTTS_IML'] = NTTS_IML
AUDIO_OBJECT['NTTS_AGC'] = NTTS_AGC
AUDIO_OBJECT['CINGO'] = CINGO
AUDIO_OBJECT['CINGO_SPK'] = CINGO_SPK
AUDIO_OBJECT['upHear Virtualizer'] = UPHEAR_VIRT
AUDIO_OBJECT['upHear VQE'] = upHear_VQE

AUDIO_OBJECT['ABS_FP'] = ABS_FP
AUDIO_OBJECT['SQRT_FP'] = SQRT_FP
AUDIO_OBJECT['MUL_FP'] = MUL_FP
AUDIO_OBJECT['IN_FP'] = IN_FP
AUDIO_OBJECT['OUT_FP'] = OUT_FP
AUDIO_OBJECT['ADDER_FP'] = OUT_FP
AUDIO_OBJECT['DELAY_FP'] = DELAY_FP
AUDIO_OBJECT['HPF_FP'] = HPF_FP
AUDIO_OBJECT['LPF_FP'] = LPF_FP
AUDIO_OBJECT['FIR_FP'] = FIR_FP
AUDIO_OBJECT['XOVER_FP'] = XOVER_FP
AUDIO_OBJECT['CLIPPER_FP'] = CLIPPER_FP
AUDIO_OBJECT['COMP_FP'] = COMP_FP
AUDIO_OBJECT['COMP_COMBO_FP'] = COMP_Combo_FP
AUDIO_OBJECT['PEQ_FP'] = PEQ_FP
AUDIO_OBJECT['LIMITER_FP'] = LIMITER_FP
AUDIO_OBJECT['GAIN_FP'] = GAIN_FP
AUDIO_OBJECT['METER_FP'] = METER_FP
AUDIO_OBJECT['MUX_FP'] = MUX_FP
AUDIO_OBJECT['MUTE_FP'] = MUTE_FP
AUDIO_OBJECT['DBASS_FP'] = DBASS_FP
AUDIO_OBJECT['IIRCOEF_FP'] = IIRCOEF_FP
AUDIO_OBJECT['MIXER_FP'] = MIXER_FP

AUDIO_OBJECT_TEMP = OrderedDict()

AUDIO_OBJECT['AIZip'] = AI_ZIP
AUDIO_OBJECT['AIZip_DialogEnhance'] = AI_ZIP_DE

AUDIO_OBJECT['BdSoundS2C'] = BD_SOUND
#########################  Wrpping Child Dict Into Parent Dict  #########################

import flowstudio.flow_conf_list_co