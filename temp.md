1. Verify each finding against current code. Fix only still-valid issues, skip the
rest with a brief reason, keep changes minimal, and validate.

In `@features/steps/revision_retroalimentacion_steps.py` around lines 287 - 294,
Update step_impl for “queda registrado en el historial de actividad” to filter
BitacoraColeccion by the specific PROPUESTA_APROBADA or PROPUESTA_RECHAZADA
action, not merely the collection. In the notification assertion step around the
referenced lines, query Notificacion for the requester and assert that a
matching notification exists rather than checking only estado.
2. Verify each finding against current code. Fix only still-valid issues, skip the
rest with a brief reason, keep changes minimal, and validate.

In `@src/materiales/models.py` around lines 1201 - 1207, Validate the requested
book’s collection membership in crear_propuesta_inclusion before calling
cls.objects.create: reject inclusion when libro is already in coleccion. Apply
the corresponding inverse validation in crear_propuesta_exclusion, rejecting
exclusion when libro is not in coleccion, while preserving the existing
participant permission checks.
3. Verify each finding against current code. Fix only still-valid issues, skip the
rest with a brief reason, keep changes minimal, and validate.

In `@src/materiales/models.py` around lines 1204 - 1222, Wrap each complete
proposal lifecycle operation in transaction.atomic(), including the creation
flow around the proposal, BitacoraColeccion audit record, and Notificacion, plus
the operations covering the referenced rejection ranges. Ensure proposal state
changes and all secondary writes commit or roll back together, preserving
existing behavior and return values.
4. Verify each finding against current code. Fix only still-valid issues, skip the
rest with a brief reason, keep changes minimal, and validate.

In `@src/materiales/models.py` around lines 1209 - 1221, Update the proposal and
corresponding notification creation paths, including the additional occurrences,
to ensure generated valores for BitacoraColeccion.detalles and
Notificacion.mensaje never exceed their field limits before saving. Safely
truncate the interpolated text while preserving valid content, or enlarge both
model fields and add the required migration; apply the same handling
consistently to all affected messages.
5. Verify each finding against current code. Fix only still-valid issues, skip the
rest with a brief reason, keep changes minimal, and validate.

In `@src/materiales/models.py` around lines 1267 - 1280, Update the proposal
approval and rejection methods containing the BitacoraColeccion and Notificacion
writes to fetch the proposal via select_for_update() within the surrounding
transaction, then validate the persisted estado on that locked instance. Apply
the state change, activity record, and notification using only the locked
proposal instance, preventing concurrent decisions from acting on stale state.