## Ambiguities

*   **"The new password must be at least 8 characters long."** (La nueva contraseña debe tener al menos 8 caracteres de longitud).
    *   *¿Por qué es un problema?* Esta frase es ambigua porque solo define la longitud, pero no especifica si existen reglas de complejidad (como el uso de mayúsculas, minúsculas, números o caracteres especiales). Si el equipo de desarrollo solo implementa el límite de longitud, un usuario podría poner "12345678" o "aaaaaaaa", lo cual es un riesgo grave de seguridad. Por el contrario, si el desarrollador decide aplicar sus propias reglas de complejidad sin avisar, el equipo de QA no sabrá qué validar y los usuarios podrían frustrarse al no entender por qué se rechaza su contraseña.
*   **"After submitting a registered email, the user receives a reset link."** (Después de enviar un correo registrado, el usuario recibe un enlace de restablecimiento).
    *   *¿Por qué es un problema?* No queda claro qué sucede en la interfaz de usuario (UI) inmediatamente después de hacer clic en el botón de enviar. ¿Se muestra un mensaje de éxito en la misma pantalla? ¿Se redirige al usuario al login? Si no se define esto, el desarrollador podría no mostrar ningún mensaje visual, lo que hará que el usuario piense que el sistema no funciona y haga clic repetidas veces, saturando el servidor de correos.

---

## Missing acceptance criteria

*   **Comportamiento ante correos no registrados (Seguridad/Enumeración de usuarios):** No se especifica qué debe hacer el sistema si el usuario ingresa un correo electrónico que no existe en la base de datos.
    *   *¿Por qué es un problema?* Si el sistema muestra un mensaje de error que dice "El correo no está registrado", un atacante malicioso podría usar esta pantalla para adivinar qué correos tienen cuentas activas en nuestra plataforma (ataque de enumeración de usuarios). Es vital definir si se mostrará un mensaje genérico ("Si el correo existe, recibirás un enlace") para proteger la privacidad.
*   **Segunda confirmación de la nueva contraseña:** La historia no menciona si el usuario debe escribir la nueva contraseña dos veces (campo "Confirmar nueva contraseña").
    *   *¿Por qué es un problema?* Sin un campo de confirmación, si el usuario comete un error de dedo (typo) al escribir su nueva contraseña oculta (con asteriscos), la guardará con el error. Al intentar iniciar sesión, no podrá entrar y se verá obligado a repetir todo el proceso de restablecimiento, generando una mala experiencia de usuario.
*   **Inactivación de sesiones activas (Sesiones concurrentes):** No se establece si el cambio de contraseña debe cerrar las sesiones activas en otros dispositivos.
    *   *¿Por qué es un problema?* Si el usuario está restableciendo su contraseña porque sospecha que alguien hackeó su cuenta, el sistema debe cerrar inmediatamente cualquier sesión abierta en otros navegadores o celulares. Si no se especifica este criterio, el atacante podría seguir dentro de la cuenta de forma indefinida.
*   **Diseño y remitente del correo electrónico:** No se definen los detalles del correo que se envía (remitente, asunto, plantilla de diseño, texto legal).
    *   *¿Por qué es un problema?* Si no se especifican estos criterios de aceptación, el desarrollador podría enviar un correo en texto plano, sin formato, o con un remitente genérico (ej. "no-reply@localhost"), lo que provocará que el correo sea clasificado como Spam por Gmail/Outlook o que el usuario desconfíe del correo por parecer phishing.

---

## Edge cases not covered

*   **Múltiples solicitudes de restablecimiento consecutivas:** El usuario hace clic en "Olvidé mi contraseña" varias veces seguidas y genera 3 correos diferentes.
    *   *¿Por qué es un problema?* Debemos definir si cada nuevo correo invalida automáticamente el enlace del correo anterior. Si no se controla esto, el usuario podría intentar usar el primer enlace recibido (que ya debería estar obsoleto) y el sistema podría fallar o permitir múltiples cambios de contraseña confusos.
*   **Uso de un enlace ya utilizado o expirado:** El usuario hace clic en el enlace después de que pasaron las 24 horas, o hace clic en un enlace que ya usó para cambiar la contraseña hace unos minutos.
    *   *¿Por qué es un problema?* El sistema no puede simplemente caerse (dar un error 500) o quedarse en blanco. Debe existir un diseño y un flujo controlado que muestre un mensaje amigable indicando que el enlace ya no es válido y ofreciendo un botón para solicitar uno nuevo.
*   **Validación de formato de correo en el formulario:** El usuario ingresa un texto que no tiene formato de correo (por ejemplo, "usuario123" o "usuario@dominio").
    *   *¿Por qué es un problema?* Si la pantalla de "Olvidé mi contraseña" no valida el formato en el cliente (frontend), enviará una petición innecesaria al servidor, gastando recursos e intentando enviar un correo a una dirección imposible, lo que puede generar errores en el servicio de mensajería.
*   **Intentar usar la misma contraseña actual:** El usuario realiza el flujo para restablecer la contraseña, pero ingresa exactamente la misma contraseña que ya tenía.
    *   *¿Por qué es un problema?* Por razones de seguridad, muchas plataformas prohíben reutilizar la contraseña actual o las últimas 3 contraseñas. Si no definimos esto, el usuario podría "restablecer" su contraseña sin cambiarla realmente, manteniendo su cuenta vulnerable si esta ya había sido comprometida.

---

## Questions for the Product Owner

1.  **¿Qué respuesta visual debe dar el sistema si el correo ingresado no existe en la base de datos?** (¿Mostraremos un mensaje de error específico o un mensaje genérico por seguridad para evitar que descubran qué correos están registrados?).
2.  **¿Cuáles son las reglas de complejidad exactas para la nueva contraseña, además de la longitud mínima de 8 caracteres?** (¿Requerirá mayúsculas, minúsculas, números, caracteres especiales o bloqueará contraseñas muy comunes?).
3.  **¿Se debe incluir un segundo campo de "Confirmar contraseña" en el formulario de restablecimiento para evitar errores de escritura?**
4.  **Cuando el usuario cambie su contraseña exitosamente, ¿debemos invalidar y cerrar automáticamente todas las sesiones activas en otros dispositivos?**
5.  **¿Qué pantalla o mensaje específico debe ver el usuario si intenta acceder a un enlace que ya expiró (más de 24 horas) o que ya fue utilizado previamente?**
6.  **Una vez que el usuario confirma la nueva contraseña con éxito, ¿cuál es el siguiente paso en el flujo?** (¿Se le inicia sesión automáticamente o se le redirige a la pantalla de login con un mensaje de éxito?).