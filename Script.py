import os
class script(object):
    START_TXT = """<b>Hola {}, {}\n\nSoy un Bot de filtro automático poderoso. Puedes usarme en tu grupo y te proporcionaré películas o series en latino, tanto en el grupo como en mensajes privados !! 🗿\n<blockquote>🌿 Mantenido por: <a href="https://t.me/NessCloud">NESS Cʟᴏᴜᴅ</a></blockquote></b>"""

    HELP_TXT = """<b>Haz clic en los botones de abajo para obtener documentación sobre módulos específicos..</b>"""

    TELE_TXT = """<b>/telegraph - envíame una imagen o video (menos de 5 MB)

Nota: este comando funciona tanto en grupos como en mensajes privados del bot</b>"""

    FSUB_TXT = """<b>• Agrégame a tu grupo y hazme administrador 😗
• Hazme administrador en tu objetivo para el canal o grupo de suscripción forzada 😉
• Envía /fsub tu_id_del_chat_objetivo
Ej: <code>/fsub -100xxxxxx</code>

Ahora está hecho. Obligaré a tus usuarios a unirse a tu canal/grupo, y no proporcionaré ningún archivo hasta que se unan a tu canal objetivo.

Para deshabilitar fsub en tu grupo, simplemente envía <code>/del_fsub</code>

Para verificar si fsub está conectado o no, usa <code>/show_fsub</code></b>"""

    FORCESUB_TEXT = """<b>
Para obtener la película solicitada por ti.

Tendrás que unirte a nuestro canal oficial.

Primero, haz clic en el botón "Unirse al Canal de Actualizaciones", luego haz clic en el botón "Re-solicitar Unirse".

Después de eso, intenta acceder a esa película y luego haz clic en el botón "intenta de nuevo".
    </b>"""

    TTS_TXT = """
<b>• Envía /tts para usar esta función</b>"""

    DISCLAIMER_TXT = """
<b>Este es un proyecto de código abierto.

Todos los archivos en este bot están disponibles libremente en Internet o publicados por otros. Para facilitar la búsqueda, este bot indexa archivos que ya están subidos en Telegram. Respetamos todas las leyes de derechos de autor y trabajamos en conformidad con DMCA y EUCD. Si algo va en contra de la ley, por favor contáctame para que se elimine lo antes posible. Está prohibido descargar, transmitir, reproducir, compartir o consumir contenido sin el permiso explícito del creador o titular legal de los derechos. Si crees que este bot está violando tu propiedad intelectual, contacta a los canales respectivos para su eliminación. El bot no posee ninguno de estos contenidos, solo indexa los archivos de Telegram. 

<blockquote>🌿 Mantenido por: <a href='https://t.me/NessCloud'>NESS Cʟᴏᴜᴅ</a></blockquote></b>"""

    ABOUT_TEXT = """<blockquote><b>
‣ Mi nombre : XinzzZ
‣ Creador : <a href='https://t.me/WayK17X'>WayK</a>
‣ Librería : Pyrogram
‣ Lenguaje : Python
‣ Base de datos : MongoDB
‣ Hospedado en  : Tu Corazón
‣ Estado de compilación : v5.2 [estable]
</b></blockquote>"""    

    SUPPORT_GRP_MOVIE_TEXT = '''<b>Hola {}

He encontrado {} resultados 🎁,
pero no puedo enviarlos aquí 🤞🏻
por favor únete a nuestro grupo de solicitudes para recibirlos ✨</b>'''

    CHANNELS = """
<u>Nuestros grupos y canales</u> 

▫ Todas las películas y series, nuevas y antiguas.
▫ Películas en todos los idiomas disponibles.
▫ Soporte siempre de administradores.
▫ Servicios 24x7 disponibles."""

    LOGO = """

BOT FUNCIONANDO CORRECTAMENTE 🔥"""

    RESTART_TXT = """
<b>¡Bot Reiniciado!
> {} 
📅 Fecha: <code>{}</code>
⏰ Hora: <code>{}</code>
🌐 Zona horaria: <code>Asia/Kolkata</code>
🛠️ Estado de compilación: <code>v4.2 [Estable]</code>

Por @NessCloud</b>"""

    STATUS_TXT = """<b><u>🗃 Base de datos 1 🗃</u>

✅ Total de usuarios - <code>{}</code>
✅ Total de grupos - <code>{}</code>
✅ Almacenamiento usado - <code>{} / {}</code>

<u>🗳 Base de datos 2 🗳</u>

✅ Total de archivos - <code>{}</code>
✅ Almacenamiento usado - <code>{} / {}</code>

<u>🤖 Detalles del bot 🤖</u>

🔹 Tiempo activo - <code>{}</code>
🔹 RAM - <code>{}%</code>
🔹 CPU - <code>{}%</code></b>"""

    NEW_USER_TXT = """<b>#Nuevo_Usuario {}

≈ ID: <code>{}</code>
≈ Nombre: {}</b>"""

    NEW_GROUP_TXT = """#Nuevo_Grupo {}

Nombre del grupo - {}
ID - <code>{}</code>
Nombre de usuario del grupo - @{}
Enlace del grupo - {}
Total de miembros - <code>{}</code>
Usuario - {}"""

    REQUEST_TXT = """<b>📜 Usuario - {}
📇 ID - <code>{}</code>

🎁 Mensaje de solicitud - <code>{}</code></b>"""  

    IMDB_TEMPLATE_TXT = """
<b>Hola {message.from_user.mention}, aquí están los resultados para tu búsqueda {search}.

🍿 | Título : {title}
🎃 | Géneros : {genres}
📆 | Año : {release_date}
⭐ | Calificación : {rating} / 10</b>
"""

    FILE_CAPTION = """<b>{file_name}\n\nÚnete a ➥ 「<a href="https://t.me/NessCloud">NESS Cloud</a>」</b>"""

    ALRT_TXT = """¡Rápido, quítate de ahí!"""

    OLD_ALRT_TXT = """Estás usando mis mensajes antiguos... envía una nueva solicitud.."""

    NO_RESULT_TXT = """<b>Este mensaje no está publicado o agregado en mi base de datos 🙄</b>"""

    I_CUDNT = """💀 Hola {}

No pude encontrar ninguna película o serie con ese nombre..🐫 """

    I_CUD_NT = """👀 Hola {}

No pude encontrar nada relacionado con eso 😞... revisa tu ortografía."""
    
    CUDNT_FND = """☠️ Hola {}

No pude encontrar nada relacionado con eso, ¿quisiste decir alguno de estos? 👇"""

    FONT_TXT = """<b>Puedes usar este modo para cambiar el estilo de tus fuentes, simplemente envíame en este formato

<code>/font hi how are you</code></b>"""

    PLAN_TEXT = """<b>Estamos ofreciendo premium a los precios más bajos:
    
1 dolar por una semana 👻
3 dolares por un mes 😚
6 dolares por tres meses 😗

Haz clic en el botón de abajo para continuar comprando ↡↡↡
</b>"""

    VERIFICATION_TEXT = """<b>👋 Hola {} {},

📌 <u>No estás verificado hoy, por favor haz clic en verificar y obtén acceso ilimitado hasta la siguiente verificación</u>

#verificación:- 1/3 ✓

Si deseas archivos directos sin ninguna verificación, compra la suscripción del bot 😊

💶 Envía /plan para comprar la suscripción</b>"""

    VERIFY_COMPLETE_TEXT = """<b>👋 Hola {},

Has completado la primera verificación ✓

Ahora tienes acceso ilimitado hasta el próximo <code>{}</code></b>"""

    SECOND_VERIFICATION_TEXT = """<b>👋 Hola {} {},

📌 <u>No estás verificado, toca el enlace de verificación y obtén acceso ilimitado hasta la siguiente verificación</u>

#verificación:- 2/3

Si deseas archivos directos sin ninguna verificación, compra la suscripción del bot 😊

💶 Envía /plan para comprar la suscripción</b>"""

    SECOND_VERIFY_COMPLETE_TEXT = """<b>👋 Hola {},

Has completado la segunda verificación ✓

Ahora tienes acceso ilimitado hasta el próximo <code>{}</code></b>"""

    THIRDT_VERIFICATION_TEXT = """<b>👋 Hola {},

📌 <u>No estás verificado hoy, toca el enlace de verificación y obtén acceso ilimitado por el día completo.</u>

#verificación:- 3/3

Si deseas archivos directos, puedes optar por el servicio premium (sin necesidad de verificar)</b>"""

    THIRDT_VERIFY_COMPLETE_TEXT= """<b>👋 Hola {},

Has completado la tercera verificación ✓

Ahora tienes acceso ilimitado por el día completo </b>"""

    VERIFIED_LOG_TEXT = """<b><u>☄ Usuario verificado con éxito ☄</u>

⚡️ | Nombre: {} [ <code>{}</code> ]
📆 | Fecha: <code>{}</code></b>

#verificado_{}_completado"""

    MOVIES_UPDATE_TXT = """<b>#Nuevo_Archivo_Agregado ✅
**🍿 | Título:** {title}
**🎃 | Géneros:** {genres}
**📆 | Año:** {year}
**⭐ | Calificación:** {rating} / 10
</b>"""

    PREPLANS_TXT = """<b>👋 Hola {},

<blockquote>🎁 Beneficios de la función premium:</blockquote>

❏ No es necesario abrir enlaces
❏ Obtén archivos directos   
❏ Experiencia sin anuncios 
❏ Enlace de descarga de alta velocidad                         
❏ Enlaces de streaming multi-reproductor                           
❏ Películas y series ilimitadas                                                                        
❏ Soporte total de administradores                              
❏ La solicitud se completará en 1h [si está disponible]

⛽️ Verifica tu plan activo: /myplan
</b>"""    

    PREPLANSS_TXT = """<b>👋 Hola {}

<blockquote>🎁 Beneficios de la función premium:</blockquote>

❏ No es necesario abrir enlaces
❏ Obtén archivos directos   
❏ Experiencia sin anuncios 
❏ Enlace de descarga de alta velocidad                         
❏ Enlaces de streaming multi-reproductor                           
❏ Películas y series ilimitadas                                                                        
❏ Soporte total de administradores                              
❏ La solicitud se completará en 1h [si está disponible]

⛽️ Verifica tu plan activo: /myplan
</b>"""

    OTHER_TXT = """<b>👋 Hola {},

🎁 <u>Otro plan</u>
⏰ Días personalizados
💸 De acuerdo a los días que elijas

🏆 Si deseas un nuevo plan aparte del dado, puedes hablar directamente con nuestro <a href='https://t.me/WayK17X'>propietario</a> haciendo clic en el botón de contacto que aparece abajo.
    
👨‍💻 Contacta al propietario para obtener tu otro plan.

➛ Usa /plan para ver todos nuestros planes de una vez.
➛ Verifica tu plan activo usando: /myplan</b>"""

    FREE_TXT = """<b>👋 Hola {}

<blockquote>🎖️Planes premium disponibles:</blockquote>

 💲 01    ➠    01 semana
 💲 03    ➠    01 mes
 💲 06   ➠     03 meses
 💲 10    ➠    06 meses
 💲 15   ➠     12 meses
 💲 25    ➠    permanente 

🆔 PayPal ➩ <code>Fifteen15ht@gmail.com</code> [haz clic para copiar]
 
⛽️ Verifica tu plan activo: /myplan

🏷️ <a href='https://t.me/jisshu_Premium_proof'>Prueba premium</a>

‼️ Debes enviar una captura de pantalla después del pago.
‼️ Danos algo de tiempo para agregarte a la lista premium.
</b>"""

    ADMIN_CMD_TXT = """<b><blockquote>
-------------Usuario Premium------------
➩ /add_premium {ID de usuario} {Tiempo} - Añadir un usuario premium
➩ /remove_premium {ID de usuario} - Eliminar un usuario premium
➩ /add_redeem - Generar un código de canje
➩ /premium_users - Listar todos los usuarios premium
➩ /refresh - Renovar la prueba gratuita para usuarios
-------------Canal de Actualizaciones----------
➩ /set_muc {ID del canal} - Establecer el canal de actualizaciones de películas
--------------Búsqueda en PM--------------
➩ /pm_search_on - Activar la búsqueda en PM
➩ /pm_search_off - Desactivar la búsqueda en PM
--------------ID de Verificación--------------
➩ /verify_id - Generar un ID de verificación para uso exclusivo en grupos
--------------Configurar Anuncios----------------
➩ /set_ads {nombre de anuncio}#{Tiempo}#{URL de foto} - <a href="https://t.me/Jisshu_developer/11">Explicación</a>
➩ /del_ads - Eliminar anuncios
-------------Tendencias Principales------------
➩ /setlist {Mirzapur, Money Heist} - <a href=https://t.me/Jisshu_developer/10>Explicación</a>
➩ /clearlist - Borrar todas las listas
</blockquote></b>"""

    ADMIN_CMD_TXT2 = """<b><blockquote>
--------------Indexar Archivos--------------
➩ /index - Indexar todos los archivos
--------------Salir del Grupo--------------
➩ /leave {ID del grupo} - Salir del grupo especificado
-------------Enviar Mensaje-------------
➩ /send {nombre de usuario} - Usa este comando como respuesta a cualquier mensaje
----------------Banear Usuario---------------
➩ /ban {nombre de usuario} - Banear al usuario 
➩ /unban {nombre de usuario} - Desbanear al usuario
--------------Difusión--------------
➩ /broadcast - Difundir un mensaje a todos los usuarios
➩ /grp_broadcast - Difundir un mensaje a todos los grupos conectados
</blockquote></b>"""

    GROUP_TEXT = """<b><blockquote>
 --------------Configurar Verificación-------------
/set_verify {enlace del sitio web} {API del sitio web}
/set_verify_2 {enlace del sitio web} {API del sitio web}
/set_verify_3 {enlace del sitio web} {API del sitio web}
-------------Configurar Tiempo de Verificación-----------
/set_time_2 {segundos} Establece el tiempo para la segunda verificación
/set_time_3 {segundos} Establece el tiempo para la tercera verificación
--------------Verificación Activar/Desactivar------------
/verifyoff {código verify.off} - Desactivar la verificación <a href="https://t.me/IM_JISSHU">CONTACTA</a> al admin del bot para un código verify.off
/verifyon - Activar la verificación 
------------Configurar Leyenda del Archivo-----------
/set_caption - Establece una leyenda personalizada para el archivo 
-----------Configurar Plantilla de IMDb-----------
/set_template - Establece la plantilla de IMDb <a href="https://t.me/Jisshu_developer/8">Ejemplo</a>
--------------Configurar Tutorial-------------
/set_tutorial - Establece el tutorial de verificación 
-------------Configurar Canal de Log-----------
--> Añade un canal de logs usando este formato y asegúrate de que el bot sea administrador en tu canal de logs 👇

/set_log {ID del canal de logs}
---------------------------------------
Puedes consultar todos tus detalles mediante el comando /details
</blockquote>
Agrégame a tu grupo, hazme administrador y utiliza todas las funciones 😇</b>"""

    SOURCE_TXT = """<b>
NOTA:
- Código fuente aquí ◉› :<blockquote><a href="https://t.me/JISSHU_BOTS">Jisshu-Filter-Bot</a></blockquote>

desarrollador : Mr.Jisshu
</b>""" 

    GROUP_C_TEXT = """<b><blockquote>
 --------------Configurar Verificación-------------
/set_verify {enlace del sitio web} {API del sitio web}
/set_verify_2 {enlace del sitio web} {API del sitio web}
/set_verify_3 {enlace del sitio web} {API del sitio web}
-------------Configurar Tiempo de Verificación-----------
/set_time_2 {segundos} Establece el tiempo para la segunda verificación
/set_time_3 {segundos} Establece el tiempo para la tercera verificación
--------------Verificación Activar/Desactivar------------
/verifyoff {código verify.off} - Desactivar la verificación <a href="https://t.me/IM_JISSHU">CONTACTA</a> al admin del bot para un código verify.off
/verifyon - Activar la verificación 
------------Configurar Leyenda del Archivo-----------
/set_caption - Establece una leyenda personalizada para el archivo 
-----------Configurar Plantilla de IMDb-----------
/set_template - Establece la plantilla de IMDb <a href="https://t.me/Jisshu_developer/8">Ejemplo</a>
--------------Configurar Tutorial-------------
/set_tutorial {enlace del tutorial} - Establece 1 tutorial de verificación 
/set_tutorial_2 {enlace del tutorial} - Establece 2 tutoriales de verificación 
/set_tutorial_3 {enlace del tutorial} - Establece 3 tutoriales de verificación 
-------------Configurar Canal de Log-----------
--> Añade un canal de logs usando este formato y asegúrate de que el bot sea administrador en tu canal de logs 👇

/set_log {ID del canal de logs}
---------------------------------------
Puedes consultar todos tus detalles mediante el comando /details
</blockquote>
Si tienes alguna duda, por favor <a href="https://t.me/IM_JISSHU">CONTACTA</a> a mi <a href="https://t.me/IM_JISSHU">administrador</a></b>"""

    SOURCE_TXT = """<b>
NOTA:
- Código fuente aquí ◉› :<blockquote><a href="https://t.me/JISSHU_BOTS">Jisshu-Filter-Bot</a></blockquote>

desarrollador : Mr.Jisshu
</b>"""