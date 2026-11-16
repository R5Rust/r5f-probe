"""Writes the probe schedule: mod/.../rp_plan.gnut (played by R5Flowstate) and plan.json (replayed by R5Rust's
probecmp example). Each run: name + events "ms:command". Commands: +x/-x console binds, JUMP:n / TAP:n = n one-frame
presses of jump / forward (a wheel flick), MARK starts logging, END stops it.
    python plan.py [--fps 60]"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPOT = (-12211, 384, 1640, 0)  # spawn hall floor (z 1580), 1400u flat and clear along +X (examples/runlen.rs); dropped from 60u up
FPS = int(sys.argv[sys.argv.index('--fps') + 1]) if '--fps' in sys.argv else 60

runs = []
def run(name, evs):
    runs.append({'name': name, 'ev': [{'t': t, 'c': c} for t, c in evs]})

run('walk', [(0, 'MARK'), (0, '+forward'), (2500, '-forward'), (3500, 'END')])
run('sprint_hold', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (2500, '-forward'), (2500, '-speed'), (3500, 'END')])
run('sprint_tap', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (40, '-speed'), (2500, '-forward'), (3500, 'END')])
run('crouch_walk', [(0, 'MARK'), (0, '+duck'), (0, '+forward'), (2000, '-forward'), (2000, '-duck'), (3000, 'END')])
run('jump_stand', [(0, 'MARK'), (300, 'JUMP:1'), (2000, 'END')])
run('sprint_jump', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (3000, '-forward'), (3000, '-speed'), (3500, 'END')])
for dt in (50, 150, 250, 350, 450):
    run(f'lurch_d_{dt}', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (1500 + dt, '-forward'),
                          (1500 + dt, '+moveright'), (2500, '-moveright'), (2500, '-speed'), (3000, 'END')])
run('lurch_a_150', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (1650, '-forward'), (1650, '+moveleft'),
                    (2500, '-moveleft'), (2500, '-speed'), (3000, 'END')])
run('lurch_s_150', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (1650, '-forward'), (1650, '+back'),
                    (2500, '-back'), (2500, '-speed'), (3000, 'END')])
run('lurch_sd_150', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (1650, '-forward'), (1650, '+back'),
                     (1650, '+moveright'), (2500, '-back'), (2500, '-moveright'), (2500, '-speed'), (3000, 'END')])
run('air_strafe_d', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (1500, '-forward'), (1500, '+moveright'),
                     (2500, '-moveright'), (2500, '-speed'), (3000, 'END')])
run('slide', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, '+duck'), (3200, '-duck'), (3200, '-forward'),
              (3200, '-speed'), (4000, 'END')])
run('slide_jump', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, '+duck'), (1800, 'JUMP:1'), (1850, '-duck'),
                   (3200, '-forward'), (3200, '-speed'), (4000, 'END')])
run('bhop', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (2283, 'JUMP:1'), (3066, 'JUMP:1'),
             (3900, '-forward'), (3900, '-speed'), (4500, 'END')])

# LiTTle's Forward RAS at reference timing, from the Lurch Trainer (C:\Code\apex\lurch-trainer\r5test\plan.json)
lt = os.path.join(r'C:\Code\apex\lurch-trainer\r5test\plan.json')
if os.path.exists(lt):
    for p in json.load(open(lt)):
        if p['name'] in ('forward-ras.ref.0', 'forward-ras.no_ts.0'):
            runs.append({'name': p['name'].replace('.', '_').replace('-', '_'), 'ev': [{'t': round(e['t']), 'c': e['c']} for e in p['ev']]})

# --shots: camera poses for render side-by-sides (feet origin, pitch, yaw), HUD and viewmodel hidden, FOV 100 (= R5Rust's)
SHOTS = [tuple(x) for x in json.load(open(os.path.join(HERE, 'poses.json')))]  # examples/posegen.rs
if '--shots' in sys.argv:
    runs = []
    CVARS = ('mat_autoexposure_compensation mat_autoexposure_max mat_autoexposure_max_luminance mat_autoexposure_max_multiplier '
             'mat_autoexposure_min mat_autoexposure_min_multiplier mat_autoexposure_speed mat_autoexposure_target_lum_max '
             'mat_autoexposure_target_lum_min mat_autoexposure_uncap mat_autoexposure_force_value mat_bloom_amount_override mat_bloom_clamp '
             'mat_bloom_cutoff mat_bloom_global_baseline mat_bloom_streak_amount mat_bloom_streak_clamp mat_bloom_streak_cutoff '
             'mat_bloom_streak_cutoff_exposure_adapt mat_bloom_streak_exponent_post mat_bloom_streak_exponent_pre mat_bloom_wide_amount '
             'mat_bloom_wide_clamp mat_bloom_wide_exponent_pre mat_colorcorrection mat_debug_tonemapping mat_debug_tonemapping_disable '
             'mat_debug_tonemapping_linear_segment_end mat_debug_tonemapping_mid1 mat_debug_tonemapping_mid2 mat_debug_tonemapping_shoulder '
             'mat_debug_tonemapping_toe mat_dynamic_tonemapping mat_exposure_interaction_override mat_gamma mat_hdr_paper_white_nits '
             'mat_hdrcolorcorrection mat_local_contrast_edge_scale_override mat_local_contrast_midtone_mask_override '
             'mat_local_contrast_scale_override mat_local_contrast_vignette_end_override mat_local_contrast_vignette_start_override '
             'mat_sharpen_amount mat_sharpen_threshold mat_sharpen_width mat_vignette_enable r_exposure fog_enable fog_enableskybox').split()
    pre = ['DUMP|' + ','.join(CVARS), 'CMD|noclip', 'CMD|cl_fovScale 1.428571', 'CMD|r_drawviewmodel 0', 'CMD|cl_drawhud 0', 'CMD|hud_setting_showHud 0']
    shots = [c for n, x0, y, z, pt, yw in SHOTS for c in (f'CMD|rp look {x0} {y} {z} {pt} {yw}', f'SHOT|{n}')]
    json.dump(SHOTS, open(os.path.join(HERE, 'shots.json'), 'w'))
setup = [f'fps_max {FPS}', f'rp tp {SPOT[0]} {SPOT[1]} {SPOT[2]} {SPOT[3]}', 'rp info']
lines = ['// GENERATED by tools/r5f-probe/plan.py. Do not hand-edit.', '#if CLIENT', 'global function RP_Plan', 'global function RP_Setup', '',
         'array<string> function RP_Setup()', '{', '\tarray<string> s']
lines += [f'\ts.append( "{c}" )' for c in setup] + ['\treturn s', '}', '', 'array<string> function RP_Plan()', '{', '\tarray<string> p']
if '--shots' in sys.argv:
    for c in pre:
        lines.append(f'	p.append( "{c}" )')
    for sh in shots:
        lines.append(f'	p.append( "{sh}" )')
for r in runs:
    spec = ';'.join(f"{e['t']}:{e['c']}" for e in r['ev'])
    lines.append(f'\tp.append( "{r["name"]}|{spec}" )')
lines += ['\treturn p', '}', '#endif', '']
open(os.path.join(HERE, 'mod/Kainz-R5RustProbe/scripts/vscripts/kainz_r5rustprobe/rp_plan.gnut'), 'w', newline='\n').write('\n'.join(lines))
if '--shots' not in sys.argv:
    json.dump({'fps': FPS, 'spot': SPOT, 'runs': runs}, open(os.path.join(HERE, 'plan.json'), 'w'), indent=1)
print(f'{len(runs)} runs, fps {FPS}')
