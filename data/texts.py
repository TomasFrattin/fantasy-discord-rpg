STARTUP_COMMANDS = [
    {"comando": "🧙 /start", "descripcion": "Crear tu personaje y elegir tu afinidad."},
    {"comando": "📜 /commands", "descripcion": "Mostrar todos los comandos disponibles."},
    {"comando": "📌 /u", "descripcion": "Abrir el menú de acciones."},
    {"comando": "⚡ /energy", "descripcion": "Mostrar tu energía actual."},
    {"comando": "🎒 /inventory", "descripcion": "Mostrar tu inventario de personaje."},
    {"comando": "🐺 /hunt (⚡)", "descripcion": "Combatir y conseguir items o morir en el intento."},
    {"comando": "🧾 /profile", "descripcion": "Mostrar tu perfil de personaje."},
    {"comando": "🧺 /forage (⚡)", "descripcion": "Recolectar materiales."},
    {"comando": "😴 /sleep (⚡)", "descripcion": "Recupera vida descansando."},
    {"comando": "🏪 /merchant", "descripcion": "Visitar al mercader para comprar objetos."},
    {"comando": "🔨 /craft", "descripcion": "Crear objetos equipables o consumibles."},
    {"comando": "🪙 /contribution", "descripcion": "Aporta una cantidad de oro a las mejoras del reino."}
]


# - `/menu`: Crea un menu con las acciones disponibles.


WELCOME_MESSAGE = """
🌌 **Bienvenido a Arkanor** 🌌
*Un mundo donde la magia y los elementos luchan por el equilibrio.*

✨ Cada elección define tu destino.  
Elige tu afinidad sabiamente y forja tu camino como héroe de este mundo.

🧙‍♂️ **¡Ha llegado el momento de decidir tu camino!** 🔮
"""

FRASES_MERCADER = [
    "🛒 **Bienvenido, joven aventurero**. ¿Qué buscas hoy? Tal vez unas flechas nuevas para tu arco, alguna espada afilada, una caña de pescar reluciente o pociones que revitalicen tu energía. ¡Todo lo que un héroe necesita lo encontrarás aquí! ⚔️🍶",
    "🌟 ¡Ah, un visitante! Veo que tus ojos brillan con ansias de aventuras. **¿Buscas armas para tus combates, herramientas para tus viajes o tal vez algún elixir mágico** que te dé fuerza y vigor? No dudes en preguntar, todo está a tu disposición.",
    "⚔️ **Saludos, valiente viajero**. Hoy traigo artículos recién llegados: flechas precisas, pociones burbujeantes, cañas de pescar resistentes y artefactos que podrían salvar tu vida. ¿Qué deseas inspeccionar primero? 🏹🪄",
    "🛡️ Bienvenido a mi humilde puesto. Aquí encontrarás **de todo para tus aventuras**: armas, pociones que sanan, cañas de pescar y objetos curiosos que podrían serte útiles. ¿Qué te interesa hoy, joven héroe? ✨",
    "🍃 **Ah, llegas justo a tiempo**. Tengo en exhibición las mejores armas, flechas, pociones y cañas de pesca que puedas imaginar. Todo preparado para aventureros como tú. ¿Por dónde quieres empezar a mirar primero? 🔮",
    "🏰 ¡Salve, viajero! Mi puesto está lleno de **tesoros y herramientas** para tu travesía: flechas, espadas, pociones de toda clase, y hasta cañas de pescar que atrapan los peces más codiciados. ¿Qué deseas llevar hoy? 🐟⚔️",
    "🌿 **Saludos, joven aventurero**. Mi mercadería no es común: cada arma afila tus habilidades, cada poción restaura tu vigor, y cada caña de pescar es un portal a la paciencia y la fortuna. ¿Qué deseas explorar primero? 🍶🛠️",
    "✨ ¡Ah, justo lo que esperaba! **Tienes la mirada de quien busca aventuras**. Mi puesto ofrece flechas, armas finas, pociones y objetos que podrían cambiar tu destino. ¿Qué deseas tomar primero? 🏹🪄",
]


ELEMENT_DESCRIPTIONS = {
    "Fuego": "🔥 **Fuego**\n_Las llamas de los volcanes eternos y la pasión que arde en los corazones._\n💥 Dominarás la chispa que ilumina la oscuridad y consume lo que se interponga en tu camino.",
    "Hielo": "❄️ **Hielo**\n_Los glaciares milenarios y la calma de la noche estrellada._\n🧊 Tu toque congela el tiempo y la mente de tus enemigos, dejando tras de sí un silencio helado.",
    "Tierra": "🌱 **Tierra**\n_Las montañas que han resistido eones y raíces que abrazan el mundo._\n🌿 Tu fuerza proviene de la solidez del suelo y la paciencia de los bosques ancestrales.",
    "Sombra": "🌑 **Sombra**\n_Los susurros en la penumbra y la noche que oculta secretos._\n🦉 Te moverás entre los pliegues del mundo sin ser visto, dominando la astucia y el misterio.",
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
    "extreme": [
        "🌟 Una energía desbordante te inunda, sintiéndote invencible y listo para cualquier desafío.",
        "⚡ Tu cuerpo vibra con una fuerza sobrenatural, como si pudieras conquistar montañas y atravesar océanos sin esfuerzo.",
        "🔥 La magia fluye en cada fibra de tu ser, otorgándote un vigor inagotable que desafía los límites humanos."
    ],
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


import random

MENSAJES_PESCA = [
    "Te adentras en las aguas tranquilas durante **{minutos}** minutos 🎣. Que la suerte te acompañe en tu pesca.",
    "El sol brilla sobre el lago 🌊 y el viento susurra entre los árboles. Pescarás durante **{minutos}** minutos. ¡Buena suerte!",
    "Encuentras un árbol bajo el que descansar 🍃 mientras lanzas la caña. Tu sesión de pesca durará **{minutos}** minutos. ¡Que salga algo grande!",
    "Te sientas en una vieja roca 🪵, tiras la caña y esperas. Pasarán **{minutos}** minutos de pura aventura piscatoria.",
    "Las aguas parecen misteriosas hoy 🐟. Estás listo para pescar durante **{minutos}** minutos. ¡Que los peces estén de tu lado!",
    "El río refleja los colores del atardecer 🌅. Tu cacería de peces durará **{minutos}** minutos. ¡A por ellos!",
    "Aventurero 🧭, tus pasos te traen a este lago sereno. Tirarás la caña durante **{minutos}** minutos, atentos a los movimientos en el agua.",
    "Hojas caen suavemente a tu alrededor 🍂 mientras pescas durante **{minutos}** minutos. Mantén los ojos abiertos y la paciencia.",
    "El sonido de las olas acompaña tu espera ⚓. Pescarás durante **{minutos}** minutos, que el mar sea generoso contigo.",
    "Entre árboles y brisa fresca 🌲, lanzas la caña. Tu pesca durará **{minutos}** minutos. ¡Que encuentres algo especial!"
]


def mensaje_inicio_pesca(minutos: int) -> str:
    return random.choice(MENSAJES_PESCA).format(minutos=minutos)

ESCAPE_CONFIG = {
    "probabilidad": 0.75, 
    "mensajes_exito": [
        "🌀 Esquivaste el ataque de la criatura y desapareciste entre las sombras.",
        "🔥 Saltaste sobre un tronco caído y lograste poner distancia entre vos y tu enemigo.",
        "🌪️ Una ráfaga de viento te impulsó fuera del alcance del monstruo, escapaste con vida.",
        "💨 Te deslizaste entre las garras del enemigo y finalmente lograste escapar."
    ],
    "mensajes_fallo": [
        "😣 Tropezaste con una raíz mientras corrías y el monstruo te alcanzó.",
        "💥 Saltaste torpemente y apenas lograste esquivar un ataque, pero no lograste escapar.",
        "🌲 Tu intento de huida fue frustrado por un obstáculo inesperado, el enemigo sigue cerca.",
        "🕳️ Caíste en un pequeño agujero mientras corrías, perdiendo tiempo y permitiendo que la criatura te acorralara."
    ]
}

ENCUENTRO_VIEJO_PESCADOR = {
    "titulo": "🎣 Un encuentro en el muelle",
    "descripcion": (
        "Te acercás lentamente al viejo muelle de madera 🪵. Las tablas crujen bajo tus pies "
        "mientras las olas golpean con suavidad 🌊, trayendo consigo el aroma salado del mar. "
        "El viento sopla constante 💨, meciendo las cuerdas y haciendo danzar las redes olvidadas.\n\n"
        "A un costado, casi confundido con el paisaje, ves a un anciano pescador 👴. Su espalda está encorvada "
        "y sus manos tiemblan mientras sostiene una vieja caña 🎣, gastada por los años y las mareas. "
        "Cada intento de lanzar el anzuelo parece una pequeña lucha contra el tiempo ⏳.\n\n"
        "Al notar tu presencia, el anciano te observa en silencio por unos segundos 👀. Luego, con una leve sonrisa, "
        "asiente lentamente.\n\n"
        "— *Hace tiempo que estas aguas ya no son para mí…* —murmura—. *Tal vez vos puedas sacar mejor provecho de esta caña.*\n\n"
        "El viejo extiende su caña rústica hacia vos 🤲. Es simple, marcada por el uso, pero todavía firme.\n"
        "¿Qué decidís hacer?"
    )
}