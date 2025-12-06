STARTUP_COMMANDS = [
    {"comando": "/start", "descripcion": "Crear tu personaje y elegir tu afinidad."},
    {"comando": "/commands", "descripcion": "Mostrar todos los comandos disponibles."},
    {"comando": "/energy", "descripcion": "Mostrar tu energía actual."},
    {"comando": "/inventory", "descripcion": "Mostrar tu inventario de personaje."},
    {"comando": "/hunt", "descripcion": "Consume energía para combatir y conseguir items o morir en el intento."},
    {"comando": "/profile", "descripcion": "Mostrar tu perfil de personaje."},
    {"comando": "/forage", "descripcion": "Gasta energía para recolectar materiales."},
    {"comando": "/sleep", "descripcion": "Recupera energía descansando."},
]
# - `/menu`: Crea un menu con las acciones disponibles.


WELCOME_MESSAGE = """
🌌 **Bienvenido a Arkanor** 🌌
*Un mundo donde la magia y los elementos luchan por el equilibrio.*

✨ Cada elección define tu destino.  
Elige tu afinidad sabiamente y forja tu camino como héroe de este mundo.

🧙‍♂️ **¡Ha llegado el momento de decidir tu camino!** 🔮
"""

ELEMENT_DESCRIPTIONS = {
    "Fuego": "🔥 **Fuego**\n_Las llamas de los volcanes eternos y la pasión que arde en los corazones._\n💥 Dominarás la chispa que ilumina la oscuridad y consume lo que se interponga en tu camino.",
    "Hielo": "❄️ **Hielo**\n_Los glaciares milenarios y la calma de la noche estrellada._\n🧊 Tu toque congela el tiempo y la mente de tus enemigos, dejando tras de sí un silencio helado.",
    "Tierra": "🌱 **Tierra**\n_Las montañas que han resistido eones y raíces que abrazan el mundo._\n🌿 Tu fuerza proviene de la solidez del suelo y la paciencia de los bosques ancestrales.",
    "Sombra": "🌑 **Sombra**\n_Los susurros en la penumbra y la noche que oculta secretos._\n🕶️ Te moverás entre los pliegues del mundo sin ser visto, dominando la astucia y el misterio.",
    "Arcano": "🔮 **Arcano**\n_Conocimiento antiguo que atraviesa los límites del tiempo._\n✨ Tu mente será faro de sabiduría y tu magia te permitirá comprender y alterar la realidad a tu voluntad."
}

RECOLECTAR_DESCRIPTIONS = [
    "🌿 Recorrés un sendero cubierto de hojas secas, y al levantar unas raíces entre la tierra húmeda, un débil destello llama tu atención.",
    "🪨 Subís por un risco rocoso mientras el viento mueve la hierba; entre las piedras, algo brillante parece haber sido olvidado.",
    "🍂 Escudriñás bajo unos arbustos densos y encontrás tesoros humildes de la naturaleza, como ramitas quebradizas y pequeñas piedras curiosas.",
    "🌞 Avanzás por un claro del bosque, y al apartar hojas marchitas, un tenue brillo entre la maleza capta tu mirada.",
    "🌳 Te agachás junto a un tronco caído y descubrís fragmentos olvidados, restos de minerales o cristales erosionados por el tiempo.",
    "🏞️ Caminás por un sendero junto al río, y entre piedras húmedas hallás objetos que parecen insignificantes, pero útiles.",
    "🕯️ Explorás una cueva pequeña y, al iluminar sus rincones, descubrís fragmentos que podrían tener algún valor.",
    "🌸 Te adentrás entre hierbas altas y flores silvestres, y algo entre la maleza capta tu atención por un instante.",
    "🐦 Siguiendo un rastro de pájaros, llegás a un claro donde el suelo revela pequeños tesoros naturales escondidos.",
    "🪵 Te apoyás en una roca y, al remover hojas secas, hallás restos curiosos que podrían servirte más adelante.",
    "🗻 Avanzás por un sendero pedregoso y notás pequeños objetos entre las grietas de las piedras y el musgo.",
    "🌬️ Caminás al borde del acantilado, y el viento mueve arena y hojas, dejando ver algún fragmento olvidado.",
    "🌲 Explorás junto a un árbol viejo y hueco, y entre sus raíces retorcidas encontrás restos de minerales y hierbas secas.",
    "💧 Siguiendo un arroyo, removés algunas piedras lisas y descubrís pequeños tesoros que el agua ha dejado atrás.",
    "🌼 Recorrés un prado tranquilo y, entre flores y pasto alto, notás destellos de objetos escondidos.",
    "⛰️ Subís a un montículo de tierra y, al mover un montón de hojas, hallás cosas olvidadas por el tiempo.",
    "🪨 Explorás una zona rocosa y húmeda, donde los líquenes cubren todo; entre ellos se distinguen fragmentos curiosos.",
    "🍁 Te adentrás en un bosque otoñal, y al apartar hojas secas y ramas caídas, descubrís pequeños restos brillantes.",
    "🌳 Caminás cerca de un árbol caído y, entre la tierra removida, hallás fragmentos que podrían ser útiles.",
    "🌒 Recorrés un sendero estrecho y sombrío, y al levantar piedras sueltas, descubrís humildes tesoros de la naturaleza.",
    "🔥 Al caminar por un sendero cerca de un volcán dormido, el suelo cálido revela fragmentos minerales resplandecientes.",
    "❄️ Entre la nieve y el hielo, pequeñas piedras y raíces aparecen como diminutos secretos del paisaje invernal.",
    "🌊 A orillas de un río cristalino, el agua deja ver brillantes fragmentos entre las piedras pulidas.",
    "🍄 Entre hongos y helechos, notás pequeñas gemas naturales escondidas bajo la vegetación.",
    "🌾 Caminás por un campo dorado, y al apartar espigas secas, descubrís fragmentos que relucen al sol.",
    "🪶 Encontrás plumas caídas de aves misteriosas mezcladas con hierba y hojas, con un leve destello mágico.",
    "🦴 Entre raíces y tierra removida, hallás huesos antiguos y fragmentos que parecen contener historia.",
    "🌌 En un claro nocturno, la luz de las estrellas ilumina pequeños destellos entre piedras y raíces.",
    "💨 El viento mueve hojas y polvo, revelando pequeñas reliquias olvidadas en un sendero abandonado.",
    "🌑 Entre la penumbra de un bosque denso, fragmentos de minerales y ramitas brillan débilmente bajo la luna."
]


ENERGY_DESCS = {
    "high": [
        "⚡ Sentís el vigor recorriendo tu cuerpo, como si la magia del mundo te impulsara.",
        "🔥 Tus pasos resuenan con fuerza heroica; podrías recorrer un reino entero sin cansarte.",
        "💥 La energía fluye en vos como una corriente arcana, nada puede frenarte."
    ],
    "mid": [
        "✨ Conservás un buen caudal de energía, suficiente para seguir explorando sin preocupaciones.",
        "🏃 Tu pulso se mantiene firme; aún podés enfrentar desafíos sin dudar.",
        "🔋 La energía sigue contigo, como una brasa constante que te impulsa hacia adelante."
    ],
    "low": [
        "😮‍💨 La vitalidad empieza a escaparse de tu cuerpo; cada movimiento requiere más esfuerzo.",
        "🥱 La fatiga te muerde los talones, recordándote que incluso los aventureros necesitan descanso.",
        "⚠️ La energía se reduce a un hilo tenue; conviene que busques un lugar seguro para reponerte."
    ],
    "zero": [
        "🔻 Tu cuerpo cede al agotamiento absoluto; la aventura debe esperar.",
        "🛌 Las fuerzas te abandonan por completo, como si una sombra drenara tu energía.",
        "💀 No queda chispa alguna en tu interior; sólo el descanso puede devolverte la vida."
    ]
}


SLEEP_DESCS = [
    "🌾 Te recostás bajo un cielo silencioso mientras una brisa suave recorre tu cuerpo. El cansancio se disuelve lentamente, como si la tierra misma te devolviera un fragmento de tu vitalidad.",
    "🍃 Encontrás un rincón tranquilo, alejándote del ruido del mundo. Cerrás los ojos y sentís cómo una cálida energía se enciende dentro tuyo, reparando cada fibra agotada.",
    "🌙 Te acomodás en un lugar seguro y dejás que el sueño te alcance. Es un descanso profundo, casi ritual, donde la vida vuelve a fluir en vos con un pulso renovado.",
    "🔥 Te envolvés en un silencio reparador. Durante unos minutos, el peso de la aventura desaparece, y cuando despertás sentís que una parte de tu fuerza retorna desde lo más hondo.",
    "🌲 Apoyás la espalda contra un tronco firme, respirás hondo y cerrás los ojos. La fatiga se disipa como una sombra, dejando que la energía renazca lentamente en tu interior."
]

DEFEAT_DESCS = [
    "⚡ Una fuerza mística te envuelve y tu alma se eleva, solo para volver a tu cuerpo.",
    "🕯️ Las luces del más allá parpadean mientras sientes un llamado a seguir adelante.",
    "🌌 Una energía ancestral te envuelve y renace tu espíritu, listo para continuar la aventura.",
    "🔥 Espíritus antiguos susurran y tu esencia regresa, fortalecida y renovada."
]