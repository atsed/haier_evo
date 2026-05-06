import weakref
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfTemperature
from homeassistant.const import TEMPERATURE
from .const import DOMAIN
from . import api


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities) -> bool:
    haier_object = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for device in haier_object.devices:
        entities.extend(device.create_entities_sensor())
    if entities:
        async_add_entities(entities)
        haier_object.write_ha_state()
    return True


class HaierSensor(SensorEntity):

    def __init__(self, device: api.HaierDevice):
        self._device = weakref.proxy(device)
        self._device_attr_name = None

        device.add_write_ha_state_callback(self.async_write_ha_state)

    @property
    def device_info(self) -> dict:
        return self._device.device_info

    @property
    def available(self) -> bool:
        return self._device.available

    @property
    def native_value(self) -> float:
        return getattr(self._device, self._device_attr_name, 0.0)


class HaierWMStepSensor(HaierSensor):

    def __init__(self, device: api.HaierWMBase, attr_code: str):
        super().__init__(device)
        self._attr_code = str(attr_code)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_attr_{self._attr_code}_sensor"
        self._attr_name = f"{device.device_name} {device.get_attr_label(self._attr_code)}"

    @property
    def native_value(self):
        value = self._device.get_attr_value(self._attr_code)
        try:
            return float(value)
        except (ValueError, TypeError):
            return value


class HaierWMProgramSensor(HaierSensor):

    def __init__(self, device: api.HaierWMBase):
        super().__init__(device)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_current_program"
        self._attr_name = f"{device.device_name} Текущая программа"

    @property
    def native_value(self):
        return self._device.current_program


class HaierWMProgramStatusSensor(HaierSensor):

    def __init__(self, device: api.HaierWMBase):
        super().__init__(device)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_current_program_status"
        self._attr_name = f"{device.device_name} Статус программы"

    @property
    def native_value(self):
        return self._device.current_program_status


class HaierWMMachineStateSensor(HaierSensor):

    def __init__(self, device: api.HaierWMBase):
        super().__init__(device)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_machine_state"
        self._attr_name = f"{device.device_name} Состояние машины"

    @property
    def native_value(self):
        return self._device.machine_mode


class HaierWMPhaseSensor(HaierSensor):

    def __init__(self, device: api.HaierWMBase):
        super().__init__(device)
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_phase"
        self._attr_name = f"{device.device_name} Фаза цикла"

    @property
    def native_value(self):
        return self._device.phase


class HaierREFTemperatureSensor(HaierSensor):
    _attr_device_class = TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, device: api.HaierREF):
        super().__init__(device)
        self._device_attr_name = "current_temperature"
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_temperature"
        self._attr_name = f"{device.device_name} Температура в помещении"


class HaierREFFridgeTemperatureSensor(HaierREFTemperatureSensor):

    def __init__(self, device: api.HaierREF):
        super().__init__(device)
        self._device_attr_name = "current_fridge_temperature"
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_fridge_temperature"
        self._attr_name = f"{device.device_name} Температура холодильной камеры"


class HaierREFFreezerTemperatureSensor(HaierREFTemperatureSensor):

    def __init__(self, device: api.HaierREF):
        super().__init__(device)
        self._device_attr_name = "current_freezer_temperature"
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_freezer_temperature"
        self._attr_name = f"{device.device_name} Температура морозильной камеры"


class HaierREFFridgeModeSensor(HaierREFTemperatureSensor):

    def __init__(self, device: api.HaierREF):
        super().__init__(device)
        self._device_attr_name = "fridge_mode"
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_fridge_mode"
        self._attr_name = f"{device.device_name} Режим холодильной камеры"

    @property
    def native_value(self) -> float:
        return float(getattr(self._device, self._device_attr_name, 0.0))


class HaierREFFreezerModeSensor(HaierREFFridgeModeSensor):

    def __init__(self, device: api.HaierREF):
        super().__init__(device)
        self._device_attr_name = "freezer_mode"
        self._attr_unique_id = f"{device.device_id}_{device.device_model}_freezer_mode"
        self._attr_name = f"{device.device_name} Режим морозильной камеры"
