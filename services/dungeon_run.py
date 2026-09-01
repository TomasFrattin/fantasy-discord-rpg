from math import ceil
from services.dungeon import elegir_boss_aleatorio



# Buffs: afinidades compatibles => multiplicador a stats
SINERGIAS = {
    ("Fuego", "Arcano"): {"atk": 1.1},      # +10% atk
    ("Tierra", "Fuego"): {"hp": 1.1},       # +10% hp
    ("Hielo", "Sombra"): {"atk": 1.05, "hp": 1.05},  # +5% atk y hp
    ("Arcano", "Sombra"): {"atk": 1.1},
    # ("Arcano", "Hielo"): {"atk": 1.05, "hp": 1.15},  # -5% atk y hp
}

# Conflictos: afinidades opuestas => reducción
CONFLICTOS = {
    ("Fuego", "Hielo"): {"atk": 0.9},       # -10% atk
    ("Arcano", "Tierra"): {"hp": 0.9},      # -10% hp
    ("Arcano", "Arcano"): {"atk": 0.9},
    ("Arcano", "Hielo"): {"atk": 0.95, "hp": 0.95},  # -5% atk y hp
}


ATK_MIN = 0.7   # -30% máximo
ATK_MAX = 1.3   # +30% máximo

HP_MIN  = 0.8   # -20%
HP_MAX  = 1.4   # +40%

def clamp(value, min_v, max_v):
    return max(min_v, min(value, max_v))

class DungeonRun:
    MAX_JUGADORES = 4

    def __init__(self, dungeon, jugadores_iniciales):
        """
        dungeon: dict con keys ['id', 'nombre', 'oro_recompensa', 'bosses']  
        jugadores_iniciales: lista de dicts con keys ['user_id','username','hp','atk','llaves']
        """
        self.dungeon = dungeon
        self.jugadores = jugadores_iniciales[:self.MAX_JUGADORES]
        self.boss = elegir_boss_aleatorio(dungeon)
        self.resultado = None  # 'victoria' o 'derrota'

    def agregar_jugador(self, jugador):
        if len(self.jugadores) >= self.MAX_JUGADORES:
            raise ValueError("La dungeon ya está llena")
        
        # if jugador["llaves"] < 1:
        #     raise ValueError(f"{jugador['username']} no tiene llave")
        # jugador["llaves"] -= 1
        
        self.jugadores.append(jugador)

    def calcular_stats_grupo(self):
        jugadores_mod, eventos, _ = self.aplicar_afinidades()  # ignoramos oro_extra aquí
        hp_total = sum(j["hp_mod"] for j in jugadores_mod)
        atk_total = sum(j["atk_mod"] for j in jugadores_mod)
        return hp_total, atk_total

    def resolver_combate(self):
        hp_total, atk_total = self.calcular_stats_grupo()
        boss_hp = self.boss["hp"] * (1 + 0.4 * (len(self.jugadores)-1))
        boss_atk = self.boss["atk"] * (1 + 0.2 * (len(self.jugadores)-1))

        turnos_grupo = ceil(boss_hp / atk_total)
        turnos_boss = ceil(hp_total / boss_atk)

        self.resultado = "victoria" if turnos_grupo <= turnos_boss else "derrota"
        return self.resultado

    def calcular_bonus_oro(self):
        jugadores_mod, eventos, oro_extra = self.aplicar_afinidades()  # recibir los 3
        # Contar cuántas sinergias hay
        sinergias = 0
        n = len(jugadores_mod)
        for i in range(n):
            for k in range(i+1, n):
                a1 = jugadores_mod[i]["afinidad"]
                a2 = jugadores_mod[k]["afinidad"]
                if (a1, a2) in SINERGIAS or (a2, a1) in SINERGIAS:
                    sinergias += 1
        return sinergias * 0.05  # +5% oro por sinergia

    def aplicar_afinidades(self):
        jugadores_mod = []
        eventos = []

        for j in self.jugadores:
            jugadores_mod.append({
                **j,
                "atk_mult": 1.0,
                "hp_mult": 1.0
            })

        n = len(jugadores_mod)

        for i in range(n):
            for k in range(i + 1, n):
                a1 = jugadores_mod[i]["afinidad"]
                a2 = jugadores_mod[k]["afinidad"]

                # SINERGIA
                mod = SINERGIAS.get((a1, a2)) or SINERGIAS.get((a2, a1))
                if mod:
                    texto = []
                    if "atk" in mod: texto.append(f"aumenta daño +{int((mod['atk']-1)*100)}%")
                    if "hp" in mod: texto.append(f"aumenta vida +{int((mod['hp']-1)*100)}%")
                    
                    eventos.append({
                        "tipo": "sinergia",
                        "afinidades": (a1, a2),
                        "mod": mod,
                        "texto": ", ".join(texto)
                    })

                    for key in mod:
                        jugadores_mod[i][f"{key}_mult"] *= mod[key]
                        jugadores_mod[k][f"{key}_mult"] *= mod[key]

                # CONFLICTO
                mod = CONFLICTOS.get((a1, a2)) or CONFLICTOS.get((a2, a1))
                if mod:
                    texto = []
                    if "atk" in mod: texto.append(f"disminuye daño {int((1-mod['atk'])*100)}%")
                    if "hp" in mod: texto.append(f"disminuye vida {int((1-mod['hp'])*100)}%")
                    
                    eventos.append({
                        "tipo": "conflicto",
                        "afinidades": (a1, a2),
                        "mod": mod,
                        "texto": ", ".join(texto)
                    })

                    for key in mod:
                        jugadores_mod[i][f"{key}_mult"] *= mod[key]
                        jugadores_mod[k][f"{key}_mult"] *= mod[key]

        # Clamp final
        for j in jugadores_mod:
            j["atk_mult"] = clamp(j["atk_mult"], ATK_MIN, ATK_MAX)
            j["hp_mult"]  = clamp(j["hp_mult"], HP_MIN, HP_MAX)

            j["atk_mod"] = int(j["damage"] * j["atk_mult"])
            j["hp_mod"]  = int(j["vida"] * j["hp_mult"])

        # Bonus de oro por diversidad de afinidades
        afinidades_unicas = set(j["afinidad"] for j in jugadores_mod)
        oro_extra = 0
        if len(afinidades_unicas) == 4:
            oro_extra = 0.1  # +10% oro si hay 4 tipos diferentes
            eventos.append({
                "tipo": "oro",
                "texto": "💰 Diversidad de afinidades: +10% oro"
            })

        return jugadores_mod, eventos, oro_extra