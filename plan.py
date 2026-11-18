"""Writes the probe schedule: mod/.../rp_plan.gnut (played by R5Flowstate) and plan.json (replayed by R5Rust's
probecmp example). Each run: name + events "ms:command". Commands: +x/-x console binds, JUMP:n / TAP:n = n one-frame
presses of jump / forward (a wheel flick), MARK starts logging, END stops it.
    python plan.py [--fps 60]"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPOT = (-12211, 384, 1640, 0)  # spawn hall floor (z 1580), 1400u flat and clear along +X (examples/runlen.rs); dropped from 60u up
FPS = int(sys.argv[sys.argv.index('--fps') + 1]) if '--fps' in sys.argv else 60

runs = []
def run(name, evs, spot=SPOT):
    """spot = (x, y, z, yaw): the probe teleports there before the run (z a little above the floor) and waits until
    the player stands still on the ground near it"""
    runs.append({'name': name, 'spot': list(spot), 'ev': [{'t': t, 'c': c} for t, c in evs]})

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
# S21 lurch details: a null input (A+D pressed together: no push), and wheel-forward spam while holding D (multi-tap)
run('lurch_null_150', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (1650, '-forward'), (1650, '+moveleft'),
                       (1650, '+moveright'), (2500, '-moveleft'), (2500, '-moveright'), (2500, '-speed'), (3000, 'END')])
run('tap_spam_d', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (1500, '-forward'), (1550, '+moveright'),
                   (1600, 'TAP:8'), (2500, '-moveright'), (2500, '-speed'), (3000, 'END')])
run('air_strafe_d', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (1500, '-forward'), (1500, '+moveright'),
                     (2500, '-moveright'), (2500, '-speed'), (3000, 'END')])
run('slide', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, '+duck'), (3200, '-duck'), (3200, '-forward'),
              (3200, '-speed'), (4000, 'END')])
run('slide_jump', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, '+duck'), (1800, 'JUMP:1'), (1850, '-duck'),
                   (3200, '-forward'), (3200, '-speed'), (4000, 'END')])
run('bhop', [(0, 'MARK'), (0, '+forward'), (0, '+speed'), (1500, 'JUMP:1'), (2283, 'JUMP:1'), (3066, 'JUMP:1'),
             (3900, '-forward'), (3900, '-speed'), (4500, 'END')])

# ---- full-movement coverage (S21 1:1 pass). Spots on real geometry come from examples/featscan.rs
W0 = (-12211, 544, 1600, 0)       # same hall, 160u to the side
run('walk_back', [(0, 'MARK'), (0, '+backward'), (2000, '-backward'), (3000, 'END')])
run('walk_side', [(0, 'MARK'), (0, '+moveright'), (2000, '-moveright'), (3000, 'END')], W0)
run('walk_diag', [(0, 'MARK'), (0, '+forward'), (0, '+moveright'), (2000, '-forward'), (2000, '-moveright'), (3000, 'END')], W0)
run('crouch_stand', [(0, 'MARK'), (0, '+duck'), (0, '+forward'), (1500, '-duck'), (3000, '-forward'), (3500, 'END')])
run('crouch_tap', [(0, 'MARK'), (0, '+forward'), (1500, '+duck'), (1600, '-duck'), (3000, '-forward'), (3500, 'END')])
run('crouch_jump', [(0, 'MARK'), (0, '+duck'), (800, 'JUMP:1'), (1500, '-duck'), (2500, 'END')])
run('jump_back', [(0, 'MARK'), (0, '+backward'), (1000, 'JUMP:1'), (2500, '-backward'), (3000, 'END')])
run('sprint_jump_duck', [(0, 'MARK'), (0, '+forward'), (1500, 'JUMP:1'), (1600, '+duck'), (2600, '-duck'), (3200, '-forward'), (3700, 'END')])
run('sprint_jump_stop', [(0, 'MARK'), (0, '+forward'), (1500, 'JUMP:1'), (1550, '-forward'), (3000, 'END')])
run('air_strafe_turn', [(0, 'MARK'), (0, 'cl_yawspeed 150'), (0, '+forward'), (1500, 'JUMP:1'), (1550, '-forward'), (1550, '+moveright'),
                        (1550, '+right'), (2300, '-right'), (2300, '-moveright'), (3000, 'END')])
run('tap_spam_turn', [(0, 'MARK'), (0, 'cl_yawspeed 150'), (0, '+forward'), (1500, 'JUMP:1'), (1550, '-forward'), (1550, '+moveleft'),
                      (1550, '+left'), (1600, 'TAP:10'), (2300, '-left'), (2300, '-moveleft'), (3000, 'END')])
run('lurch_d_turn', [(0, 'MARK'), (0, 'cl_yawspeed 150'), (0, '+forward'), (1500, 'JUMP:1'), (1500, '+right'), (1650, '-forward'),
                     (1650, '+moveright'), (2200, '-right'), (2500, '-moveright'), (3000, 'END')])
run('lurch_wd_150', [(0, 'MARK'), (0, '+forward'), (1500, 'JUMP:1'), (1650, '+moveright'), (2500, '-moveright'), (2500, '-forward'), (3000, 'END')])
run('slide_long', [(0, 'MARK'), (0, '+forward'), (1500, '+duck'), (4500, '-duck'), (4500, '-forward'), (5000, 'END')])
run('slide_no_w', [(0, 'MARK'), (0, '+forward'), (1500, '+duck'), (1700, '-forward'), (4000, '-duck'), (4500, 'END')])
run('slide_side', [(0, 'MARK'), (0, '+forward'), (1500, '+duck'), (1700, '-forward'), (1700, '+moveright'), (3500, '-duck'), (3500, '-moveright'), (4000, 'END')])
run('slide_jump_late', [(0, 'MARK'), (0, '+forward'), (1500, '+duck'), (2400, 'JUMP:1'), (2450, '-duck'), (3500, '-forward'), (4000, 'END')])
run('slide_cooldown', [(0, 'MARK'), (0, '+forward'), (1500, '+duck'), (1900, '-duck'), (2600, '+duck'), (3300, '-duck'), (4000, '-forward'), (4500, 'END')])
run('jump_land_slide', [(0, 'MARK'), (0, '+forward'), (1500, 'JUMP:1'), (1700, '+duck'), (3200, '-duck'), (3200, '-forward'), (3700, 'END')])
run('bhop_slide', [(0, 'MARK'), (0, '+forward'), (1500, '+duck'), (1700, 'JUMP:1'), (1720, '-duck'), (2150, '+duck'), (2400, 'JUMP:1'),
                   (2420, '-duck'), (2850, '+duck'), (3300, '-duck'), (3800, '-forward'), (4300, 'END')])
run('bhop_fast', [(0, 'MARK'), (0, '+forward'), (1500, 'JUMP:1'), (2230, 'JUMP:3'), (2960, 'JUMP:3'), (3690, 'JUMP:3'), (4300, '-forward'), (4800, 'END')])
# walking off ledges and landing (landing slowdown / no-sprint window)
DROP_HI = (-10404, 88, 1600, 0)   # 215u drop after ~57u
DROP_LO = (-10404, 88, 1600, 90)  # 71u drop after ~250u
run('drop_215', [(0, 'MARK'), (0, '+forward'), (2500, '-forward'), (3200, 'END')], DROP_HI)
run('drop_71', [(0, 'MARK'), (0, '+forward'), (2500, '-forward'), (3200, 'END')], DROP_LO)
run('drop_71_jump', [(0, 'MARK'), (0, '+forward'), (700, 'JUMP:1'), (2500, '-forward'), (3200, 'END')], DROP_LO)
# step up, slopes
run('step_13', [(0, 'MARK'), (0, '+forward'), (1500, '-forward'), (2200, 'END')], (-12051, 544, 1600, 180))
run('slope_up', [(0, 'MARK'), (0, '+forward'), (1800, '-forward'), (2500, 'END')], (-9900, -40, 1300, 180))
run('slope_down', [(0, 'MARK'), (0, '+forward'), (1500, '-forward'), (2200, 'END')], (-10330, -40, 1470, 0))
run('slope_slide', [(0, 'MARK'), (0, '+forward'), (300, '+duck'), (2500, '-duck'), (2500, '-forward'), (3000, 'END')], (-10330, -40, 1470, 0))
run('slope_jump_up', [(0, 'MARK'), (0, '+forward'), (1150, 'JUMP:1'), (1800, '-forward'), (2500, 'END')], (-9900, -40, 1300, 180))
# mantles (jump into a ledge), mantle boost and superglide timings
M_HI = (-10416, 460, 1510, 90)    # 77.5u ledge 248u ahead (geoscan)
M_LO = (-10480, 460, 1545, 90)    # 41.4u ledge 248u ahead
run('mantle_hi', [(0, 'MARK'), (0, '+forward'), (750, 'JUMP:1'), (2000, '-forward'), (2600, 'END')], M_HI)
run('mantle_hi_late', [(0, 'MARK'), (0, '+forward'), (850, 'JUMP:1'), (2000, '-forward'), (2600, 'END')], M_HI)
M_HI_NEAR = (-10416, 668, 1510, 90)  # 40u in front of the 77.5u ledge
run('mantle_hi_stand', [(0, 'MARK'), (300, '+forward'), (300, 'JUMP:1'), (1800, '-forward'), (2400, 'END')], M_HI_NEAR)
run('mantle_lo', [(0, 'MARK'), (0, '+forward'), (700, 'JUMP:1'), (1800, '-forward'), (2400, 'END')], M_LO)
run('mantle_lo_late', [(0, 'MARK'), (0, '+forward'), (850, 'JUMP:1'), (1800, '-forward'), (2400, 'END')], M_LO)
M_LO_NEAR = (-10480, 668, 1545, 90)  # 40u in front of the 41u ledge
run('mantle_lo_stand', [(0, 'MARK'), (300, '+forward'), (300, 'JUMP:1'), (1800, '-forward'), (2400, 'END')], M_LO_NEAR)
for j in (650, 700, 750, 800, 850, 900):
    run(f'mantle_boost_{j}', [(0, 'MARK'), (300, '+forward'), (300, 'JUMP:1'), (j, 'JUMP:1'), (2000, '-forward'), (2600, 'END')], M_HI_NEAR)
    run(f'superglide_{j}', [(0, 'MARK'), (300, '+forward'), (300, 'JUMP:1'), (j, 'JUMP:1'), (j + 16, '+duck'), (j + 400, '-duck'),
                            (2000, '-forward'), (2600, 'END')], M_HI_NEAR)
# a 94.6u block: too tall for a jump + air step, so it has to be mantled
M_TALL = (-11352, -716, 1600, 180)      # face 264u ahead
M_TALL_NEAR = (-11576, -716, 1600, 180) # 40u in front of it
run('mantle_tall', [(0, 'MARK'), (0, '+forward'), (700, 'JUMP:1'), (2200, '-forward'), (2800, 'END')], M_TALL)
run('mantle_tall_stand', [(0, 'MARK'), (300, '+forward'), (300, 'JUMP:1'), (2000, '-forward'), (2600, 'END')], M_TALL_NEAR)
run('mantle_tall_release', [(0, 'MARK'), (300, '+forward'), (300, 'JUMP:1'), (750, '-forward'), (1600, '+backward'), (1700, '-backward'), (2600, 'END')], M_TALL_NEAR)
for j in (700, 800, 900):
    run(f'mantle_tall_jump_{j}', [(0, 'MARK'), (300, '+forward'), (300, 'JUMP:1'), (j, 'JUMP:1'), (2000, '-forward'), (2600, 'END')], M_TALL_NEAR)
    run(f'superglide_tall_{j}', [(0, 'MARK'), (300, '+forward'), (300, 'JUMP:1'), (j, 'JUMP:1'), (j + 16, '+duck'), (j + 400, '-duck'),
                                 (2000, '-forward'), (2600, 'END')], M_TALL_NEAR)
# the R5Flowstate SDK mantle boost (Kainz's profile has mantle_boost_input_setting 0 = off): switched on to jump for
# these runs and back off at their end (and again after the last run)
for j in (850, 900, 950, 1000):
    run(f'boost_on_tall_{j}', [(0, 'mantle_boost_input_setting 1'), (0, 'MARK'), (300, '+forward'), (300, 'JUMP:1'), (j, 'JUMP:1'),
                               (2000, '-forward'), (2600, 'END'), (2600, 'mantle_boost_input_setting 0')], M_TALL_NEAR)
# wall climb on the hall's 1100u wall
CLIMB = (-12211, 384, 1600, 90)   # the hall's 1100u wall, 357u ahead (featscan)
run('climb', [(0, 'MARK'), (0, '+forward'), (1150, 'JUMP:1'), (3500, '-forward'), (4200, 'END')], CLIMB)
run('climb_walljump', [(0, 'MARK'), (0, '+forward'), (1150, 'JUMP:1'), (1900, 'JUMP:1'), (3500, '-forward'), (4200, 'END')], CLIMB)
run('climb_walljump_back', [(0, 'MARK'), (0, '+forward'), (1150, 'JUMP:1'), (1850, '-forward'), (1850, '+backward'), (1900, 'JUMP:1'),
                            (2500, '-backward'), (3500, 'END')], CLIMB)
run('climb_release', [(0, 'MARK'), (0, '+forward'), (1150, 'JUMP:1'), (1900, '-forward'), (3500, 'END')], CLIMB)

# LiTTle's Forward RAS at reference timing, from the Lurch Trainer (C:\Code\apex\lurch-trainer\r5test\plan.json)
lt = os.path.join(r'C:\Code\apex\lurch-trainer\r5test\plan.json')
if os.path.exists(lt):
    for p in json.load(open(lt)):
        if p['name'] in ('forward-ras.ref.0', 'forward-ras.no_ts.0'):
            # JUMP / TAP carry their wheel-notch count in 'n' (the probe needs "JUMP:n"; a bare JUMP was a script error)
            runs.append({'name': p['name'].replace('.', '_').replace('-', '_'), 'spot': list(SPOT),
                         'ev': [{'t': round(e['t']), 'c': f"{e['c']}:{e['n']}" if 'n' in e else e['c']} for e in p['ev']]})

# --shots: camera poses for render side-by-sides (feet origin, pitch, yaw), HUD and viewmodel hidden, FOV 100 (= R5Rust's)
SHOTS = [tuple(x) for x in json.load(open(os.path.join(HERE, 'poses.json')))]  # examples/posegen.rs
# --only patch1,patch2: capture just these poses (a full pass re-shoots all of them)
if '--only' in sys.argv:
    ONLY = sys.argv[sys.argv.index('--only') + 1].split(',')
    SHOTS = [s for s in SHOTS if s[0] in ONLY]
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
LEGEND = next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == '--legend'), 'character_octane')  # Lifeline can't lurch
setup = [f'fps_max {FPS}', f'rp legend {LEGEND}', f'rp tp {SPOT[0]} {SPOT[1]} {SPOT[2]} {SPOT[3]}', 'rp info']
lines = ['// GENERATED by tools/r5f-probe/plan.py. Do not hand-edit.', '#if CLIENT', 'global function RP_Plan', 'global function RP_Setup', '',
         'array<string> function RP_Setup()', '{', '\tarray<string> s']
lines += [f'\ts.append( "{c}" )' for c in setup] + ['\treturn s', '}', '', 'array<string> function RP_Plan()', '{', '\tarray<string> p']
# live lurch cvars (the S21 defaults are in crates/shared/src/settings.rs; this records what R5Flowstate really runs)
GRACE = ('jump_graceperiodmax jump_graceperiodmin jump_grace_strength jump_grace_max jump_grace_cutoff_speed jump_grace_require_tap '
         'jump_grace_jump jump_grace_min_tap_period jump_grace_max_tap_count jump_grace_decay_start_tap_count jump_grace_multi_tap_decay '
         'jump_grace_multi_tap_decay_velocity_based_max_decay jump_grace_multi_tap_decay_velocity_based_max_speed '
         'jump_grace_multi_tap_decay_velocity_based_easing_type jump_grace_limit_to_90 jump_grace_controller_disable_duration '
         'jump_graceperiod mantle_boost_enabled mantle_boost_disables_tap_strafes mantle_boost_min_valid_traversal_frac '
         'bridge_mantle_boost_sprint_mult bridge_mantle_boost_jump_height mantle_boost_input_setting cl_yawspeed player_setting_autosprint '
         'sv_gravity slide_max_angle_dot skip_speed_reduce automantle_enable traversal_enable wallrun_enable').split()
if '--shots' not in sys.argv:
    lines.append(f'	p.append( "DUMP|{",".join(GRACE)}" )')
if '--shots' in sys.argv:
    for c in pre:
        lines.append(f'	p.append( "{c}" )')
    for sh in shots:
        lines.append(f'	p.append( "{sh}" )')
for r in runs:
    spec = ';'.join(f"{e['t']}:{e['c']}" for e in r['ev'])
    sp = ' '.join(str(v) for v in r['spot'])
    lines.append(f'\tp.append( "{r["name"]}|{spec}|{sp}" )')
if '--shots' not in sys.argv:
    lines.append('\tp.append( "CMD|mantle_boost_input_setting 0" )')  # never leave the boost runs' setting behind
lines += ['\treturn p', '}', '#endif', '']
open(os.path.join(HERE, 'mod/Kainz-R5RustProbe/scripts/vscripts/kainz_r5rustprobe/rp_plan.gnut'), 'w', newline='\n').write('\n'.join(lines))
if '--shots' not in sys.argv:
    json.dump({'fps': FPS, 'spot': SPOT, 'runs': runs}, open(os.path.join(HERE, 'plan.json'), 'w'), indent=1)
print(f'{len(runs)} runs, fps {FPS}')
