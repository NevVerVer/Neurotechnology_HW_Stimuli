import os
import numpy as np
import pandas as pd
import json

from psychopy import visual, core, event # import some libraries from PsychoPy
from psychopy.hardware import keyboard
from itertools import product


config = json.load(open('./config.json'))

stimuli = list(product(config['text']['words'], config['text']['colors']))
stimuli *= 10 # 10 times each stimuli
np.random.shuffle(stimuli) # shuffle in random order

trialClock = core.Clock()
win = visual.Window(
    [800,600],
    monitor="testMonitor",
    winType='pyglet',
    allowStencil=False,
    color='black',
    colorSpace='rgb',
    blendMode='avg',
    useFBO=True,
    units='deg'
    )


# create a default keyboard (e.g. to check for escape)
kb = keyboard.Keyboard(clock=trialClock)
kb.start()

# create some stimuli
instruction = visual.TextStim(win, alignText='center', text=config['text']['instruction'])
cross = visual.TextStim(win, alignText='center', color='white', text='+')
cross.size = 10.0
word = visual.TextStim(win, text="red", color="red", alignText='center')
word.size = 2.0
rectangle = visual.Polygon(win, edges=4, fillColor='white', pos=(400, 300))
# draw the stimuli and update the window
instruction.draw()
win.flip()

while True: # this creates a never-ending loop
    if len(event.getKeys())>0:
        break
    event.clearEvents()

cross.draw()
win.flip()
core.wait(5.0)
trialClock.reset()

data = []
timestamps = []
for text, color in stimuli:
    word.text = text
    word.color = color
    word.draw()
    win.flip()
    timestamps.append(trialClock.getTime())
    keys = kb.waitKeys(keyList=['r', 'g', 'b', 'y', 'escape'])
    if 'escape' in keys:
        break
    assert len(keys) == 1, "More than 1 key was pressed"
    data.append(keys[0])
    cross.draw()
    win.flip()
    core.wait(2.0)

processed_data = []
for i, key in enumerate(data):
    word, color = stimuli[i]
    processed_data.append([
        i+1,
        word,
        color,
        int(word == color),
        timestamps[i],
        key.name,
        key.rt,
        key.rt-timestamps[i],
        int(color[0]==key.name)])

columns=[
    'Stim number',
    'word', 'color',
    'is congruent',
    'Stim timestamp',
    'key pressed',
    'key timestamp',
    'delta T',
    'is correct'
    ]

save_dir = config['save_dir']
processed_data = pd.DataFrame.from_records(processed_data, columns=columns)
processed_data.to_csv(os.path.join(save_dir, 'results.csv'))
# cleanup
win.close()
core.quit()
