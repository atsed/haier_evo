import weakref
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from . import api


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities) -> bool:
    haier_object = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for device in haier_object.devices:
        entities.extend(device.create_entities_button())
    async_add_entities(entities)
    return True


class HaierButton(ButtonEntity):
    _attr_should_poll = False

    def __init__(self, device: api.HaierDevice) -> None:
        self._device = weakref.proxy(device)
        device.add_write_ha_state_callback(self.async_write_ha_state)

    @property
    def device_info(self) -> dict:
        return self._device.device_info

    @property
    def available(self) -> bool:
        return self._device.available


class HaierWMStartButton(HaierButton):
    _attr_icon = "mdi:play"

    def __init__(self, device: api.HaierWMBase) -> None:
        super().__init__(device)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_wm_start"
        self._attr_name = f"{device.device_name} Старт"

    async def async_press(self) -> None:
        await self.hass.async_add_executor_job(self._device.start_program)


class HaierWMPauseButton(HaierButton):
    _attr_icon = "mdi:pause"

    def __init__(self, device: api.HaierWMBase) -> None:
        super().__init__(device)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_wm_pause"
        self._attr_name = f"{device.device_name} Пауза"

    async def async_press(self) -> None:
        if self._device.is_paused:
            await self.hass.async_add_executor_job(self._device.resume_program)
        else:
            await self.hass.async_add_executor_job(self._device.pause_program)


class HaierWMCancelButton(HaierButton):
    _attr_icon = "mdi:stop"

    def __init__(self, device: api.HaierWMBase) -> None:
        super().__init__(device)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_wm_cancel"
        self._attr_name = f"{device.device_name} Отмена"

    async def async_press(self) -> None:
        await self.hass.async_add_executor_job(self._device.cancel_program)
