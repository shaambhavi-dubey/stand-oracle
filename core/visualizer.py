# core/visualizer.py

import numpy as np
import matplotlib.pyplot as plt

class StandVisualizer:
    def generate_radar_chart(self, stand_metadata):
        # Match lowercase excel columns perfectly
        categories = ['Destructive', 'Speed', 'Range', 'Stamina', 'Precision', 'Dev']
        stat_mapping = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'None': 0, 'Unknown': 0}
        
        values = []
        for cat in categories:
            raw_val = str(stand_metadata.get(cat, 'E')).upper().strip()
            values.append(stat_mapping.get(raw_val, 1))
            
        num_vars = len(categories)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color="purple", alpha=0.25)
        ax.plot(angles, values, color="magenta", linewidth=2)
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angles[:-1], [c.capitalize() if c != 'dev' else 'Potential' for c in categories], color='white', size=10)
        ax.set_rlabel_position(0)
        plt.yticks([1, 2, 3, 4, 5], ["E", "D", "C", "B", "A"], color="grey", size=7)
        plt.ylim(0, 5)
        
        fig.patch.set_facecolor('#0e1117')
        ax.set_facecolor('#1f242d')
        ax.spines['polar'].set_color('#444444')
        ax.grid(color='#444444', linestyle='--')
        
        return fig