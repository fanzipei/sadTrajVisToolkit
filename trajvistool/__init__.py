import folium as fl
import pandas as pd
import random

from folium.plugins import TimestampedGeoJson


def random_color(size=None):
    if size is None:
        return '#%06x' % random.randint(0, 256 * 256 * 256 - 1)
    else:
        return ['#%06x' % random.randint(0, 256 * 256 * 256 - 1) for _ in range(size)]

    
def create_map(lat=35.5, lon=139.5, zoom_start=10):
    return fl.Map(location=[lat, lon], zoom_start=zoom_start)


def single_user_df2trajdict(df_u):
    df_u = df_u.sort_values('times')
    return {
        'coordinates': df_u[['lat', 'lon']].values.tolist(),
        'times': df_u['times'].values.tolist()
    }


def df2trajdict(df_traj):
    assert ('lat' in df_traj.columns) and ('lon' in df_traj.columns) and ('times' in df_traj.columns), 'lat, lon and times are required columns'
    if 'uid' in df_traj.columns:
        # multiple users
        trajs = list(map(lambda pair: single_user_df2trajdict(pair[1]), df_traj.groupby('uid')))
    else:
        trajs = [single_user_df2trajdict(df_traj)]
    return trajs

        
def visualize_traj(trajs, fmap=None, animation=True, color='blue', weight=3, icon='circle', transition_time=100, period='PT2M', duration=None):
    if fmap is None:
        fmap = create_map()

    if type(trajs) == pd.core.frame.DataFrame:
        
        trajs = df2trajdict(trajs)
        
        if type(color) == list:
            assert len(color) == len(trajs), 'Wrong color parameter'
        else:
            if color is None:
                color = random_color(len(trajs))
            else:
                color = [color] * len(trajs)
        
        if type(weight) == list:
            assert len(weight) == len(trajs), 'Wrong weight parameter'
        else:
            weight = [weight] * len(trajs)
        
        if type(icon) == list:
            assert len(icon) == len(trajs), 'Wrong icon parameter'
        else:
            icon = [icon] * len(trajs)
            
    elif type(trajs) == dict:
        
        trajs = [trajs]
        
        if color is None:
            color = random_color(1)
        else:
            color = [color] if type(color) != list else color
        assert len(color) == 1, 'Wrong color parameter'
        
        weight = [weight] if type(weight) != list else weight
        assert len(weight) == 1, 'Wrong weight parameter'
        
        icon = [icon] if type(icon) != list else weight
        assert len(icon) == 1, 'Wrong icon parameter'
        
    elif type(trajs) == list:
        
        for traj in trajs:
            assert type(traj) == dict, 'Unsupported trajectory format'
        
        if color is None:
            color = random_color(len(trajs))
        elif type(color) == list:
            assert len(color) == len(trajs), 'Wrong color parameter'
        else:
            color = [color] * len(trajs)
        
        if type(weight) == list:
            assert len(weight) == len(trajs), 'Wrong weight parameter'
        else:
            weight = [weight] * len(trajs)
        
        if type(icon) == list:
            assert len(icon) == len(trajs), 'Wrong icon parameter'
        else:
            icon = [icon] * len(trajs)
            
    else:
        print('Unsupported trajectory format')
        
    if animation:
        TimestampedGeoJson({
            'type': 'FeatureCollection',
            'features': 
            [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': list(map(lambda x: [x[1], x[0]], traj['coordinates']))
                    },
                    'properties':{
                        'times': traj['times'],
                        'style': {
                            'color': c,
                            'weight': w
                        },
                        'icon': ic
                    }
                }
            for traj, c, w, ic in zip(trajs, color, weight, icon)]
        }, transition_time=transition_time, period=period, duration=duration).add_to(fmap)
    else:
        for traj in trajs:
            fl.PolyLine(traj['coordinates'], color=color, weight=weight).add_to(fmap)
            fl.Circle(traj['coordinates'][-1], color=color, weight=weight, radius=600).add_to(fmap)
    
    return fmap