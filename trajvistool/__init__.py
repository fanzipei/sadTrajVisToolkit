import folium as fl

from folium.plugins import TimestampedGeoJson

def create_map(lat=35.5, lon=139.5, zoom_start=10):
    return fl.Map(location=[lat, lon], zoom_start=zoom_start)

def visualize_traj(traj, fmap=None, animation=True, color='blue', weight=3, icon='circle', transition_time=100, period='PT2M', duration=None):
    if fmap is None:
        fmap = create_map()

    if animation:
        TimestampedGeoJson({
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': list(map(lambda x: [x[1], x[0]], traj['coordinates']))
                    },
                    'properties':{
                        'times': traj['times'],
                        'style': {
                            'color': color,
                            'weight': weight
                        },
                        'icon': icon
                    }
                }
            ]
        }, transition_time=transition_time, period=period, duration=duration).add_to(fmap)
    else:
        fl.PolyLine(traj['coordinates'], color=color, weight=weight).add_to(fmap)
        fl.Circle(traj['coordinates'][-1], color=color, weight=weight, radius=600).add_to(fmap)
    
    return fmap