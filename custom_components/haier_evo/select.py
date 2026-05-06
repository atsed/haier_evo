import weakref
from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from . import api


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities) -> bool:
    haier_object = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for device in haier_object.devices:
        entities.extend(device.create_entities_select())
    if entities:
        async_add_entities(entities)
        haier_object.write_ha_state()
    return True


class HaierSelect(SelectEntity):
    _attr_should_poll = False
    _attr_icon = "mdi:format-list-bulleted"

    def __init__(self, device: api.HaierDevice) -> None:
        self._device = weakref.proxy(device)
        self._device_attr_name = None
        self._attr_options = []

        device.add_write_ha_state_callback(self.async_write_ha_state)

    @property
    def device_info(self) -> dict:
        return self._device.device_info

    @property
    def available(self) -> bool:
        return self._device.available

    @property
    def current_option(self) -> str:
        return getattr(self._device, self._device_attr_name, None)

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(self.set_option, option)

    def set_option(self, value) -> None:
        method = getattr(self._device, f"set_{self._device_attr_name}", None)
        if method is not None:
            method(value)


class HaierWMListSelect(HaierSelect):

    def __init__(self, device: api.HaierWMBase, attr_code: str) -> None:
        super().__init__(device)
        self._attr_code = str(attr_code)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_attr_{self._attr_code}_select"
        self._attr_name = f"{device.device_name} {device.get_attr_label(self._attr_code)}"
        self._attr_options = device.get_attr_option_names(self._attr_code)

    @property
    def current_option(self) -> str:
        return self._device.get_attr_current_option_name(self._attr_code)

    def set_option(self, value) -> None:
        option_value = self._device.get_attr_option_value(self._attr_code, str(value))
        self._device.set_attr_option(self._attr_code, option_value)


class HaierWMProgramSelect(HaierSelect):

    def __init__(self, device: api.HaierWMBase) -> None:
        super().__init__(device)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_program_select"
        self._attr_name = f"{device.device_name} Программа"
        self._attr_options = device.get_program_options()

    @property
    def current_option(self) -> str:
        current = self._device.current_program
        return current if current in self._attr_options else None

    def set_option(self, value) -> None:
        self._device.select_program(str(value))


class HaierACEcoSensorSelect(HaierSelect):
    _attr_translation_key = "conditioner_eco_sensor"

    def __init__(self, device: api.HaierAC) -> None:
        super().__init__(device)
        self._device_attr_name = "eco_sensor"
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_eco_sensor"
        self._attr_name = f"{device.device_name} Эко-датчик"
        self._attr_options = device.get_eco_sensor_options()


class HaierREFFridgeModeSelect(HaierSelect):

    def __init__(self, device: api.HaierREF) -> None:
        super().__init__(device)
        self._device_attr_name = "fridge_mode"
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_fridge_mode_select"
        self._attr_name = f"{device.device_name} Режим холодильной камеры"
        self._attr_options = device.get_fridge_mode_options()


class HaierREFFreezerModeSelect(HaierSelect):

    def __init__(self, device: api.HaierREF) -> None:
        super().__init__(device)
        self._device_attr_name = "freezer_mode"
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_freezer_mode_select"
        self._attr_name = f"{device.device_name} Режим морозильной камеры"
        self._attr_options = device.get_freezer_mode_options()


class HaierREFMyZoneSelect(HaierSelect):

    def __init__(self, device: api.HaierREF) -> None:
        super().__init__(device)
        self._device_attr_name = "my_zone"
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_my_zone"
        self._attr_name = f"{device.device_name} My Zone"
        self._attr_options = device.get_my_zone_options()
