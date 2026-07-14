## Summary
Esta historia de usuario permite a los usuarios que ya están registrados en el sistema restablecer su contraseña de manera autónoma si la han olvidado. El objetivo principal es que el usuario pueda recuperar el acceso a su cuenta de forma segura mediante un enlace enviado a su correo electrónico.

## Acceptance criteria
Basándonos estrictamente en el texto de la historia, podemos extraer los siguientes criterios de aceptación:
- El enlace "¿Olvidó su contraseña?" ("Forgot password?") debe ser visible en la pantalla de inicio de sesión.
- Tras ingresar y enviar un correo electrónico que esté registrado en el sistema, el usuario debe recibir un enlace de restablecimiento.
- El enlace de restablecimiento de contraseña debe dejar de funcionar (expirar) exactamente después de 24 horas de haber sido enviado.
- El sistema debe validar que la nueva contraseña que elija el usuario tenga una longitud mínima de 8 caracteres.

*Nota de QA:* La historia no menciona qué debe ocurrir si el correo ingresado no está registrado, si el enlace se usa más de una vez, o si hay un diseño específico para el correo. Al estar la historia en silencio sobre esto, no debemos asumir ninguna solución.

## INVEST assessment

| Criterion | Verdict | Justification |
| :--- | :---: | :--- |
| **Independent** (Independiente) | ✅ | Esta historia se puede desarrollar y probar por sí misma, siempre y cuando ya exista la pantalla de inicio de sesión. No necesita que otras historias complejas se terminen primero. |
| **Negotiable** (Negociable) | ✅ | Los detalles específicos (como el límite de 24 horas para el enlace o la longitud de 8 caracteres de la contraseña) son puntos que el equipo de desarrollo y el dueño del producto (PO) pueden discutir y cambiar si es necesario antes de programar. |
| **Valuable** (Valiosa) | ✅ | Tiene un valor muy claro para el usuario final, ya que le permite resolver por sí mismo un problema común (olvidar la contraseña) sin tener que contactar al soporte técnico. |
| **Estimable** (Estimable) | ✅ | Al ser una funcionalidad estándar de desarrollo web y contar con reglas claras (8 caracteres, 24 horas), los desarrolladores tienen suficiente información para calcular cuánto tiempo y esfuerzo les tomará construirla. |
| **Small** (Pequeña) | ✅ | El alcance de la historia es bastante acotado. Se enfoca únicamente en el flujo de recuperación, lo que permite que se complete fácilmente dentro de un solo ciclo de trabajo (Sprint). |
| **Testable** (Testeable) | ⚠️ | Aunque los criterios son específicos (podemos medir las 24 horas y contar los 8 caracteres), la historia tiene un "Warning" (advertencia) porque no especifica los escenarios de error. Para un QA, es difícil diseñar pruebas completas si no sabemos qué pasa en el "camino triste" (por ejemplo, si el usuario escribe un correo que no existe). |

## Testability verdict
Como QA, **sí podemos comenzar a diseñar las pruebas básicas** (el "camino feliz" donde todo funciona bien), pero tenemos un bloqueador importante para terminar nuestro trabajo: **la falta de definición para los escenarios alternativos y de error (caminos tristes)**. El principal bloqueador es que la historia no dice qué debe mostrar el sistema si el usuario ingresa un correo electrónico que no existe en la base de datos (¿debemos mostrar un mensaje de error o, por seguridad, decir que el correo fue enviado de todos modos?). Sin esta definición, no podemos escribir casos de prueba exactos para validar la seguridad y la experiencia del usuario en situaciones de error.