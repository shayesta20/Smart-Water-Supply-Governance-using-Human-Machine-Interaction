# Smart Water Supply Governance using Human-Machine Interaction

## Overview
A comprehensive **Water Tank Monitoring System** with an intuitive card-based HMI interface. This project enables real-time monitoring and management of community water supplies, featuring multi-villa tracking, automated motor control, and smart usage advisories.

## Features

### 🌊 Core Functionality
- **Real-time Water Level Monitoring** - Track tank water levels with visual feedback
- **Status-based Alerts** - Color-coded status indicators (Critical, Low, Moderate, Good, Full)
- **Automated Motor Control** - Smart pump control with ON/OFF capabilities
- **Water Usage Tracking** - Monitor water consumption and inflow/outflow rates
- **Multi-Villa Support** - Manage water supply for up to 6 villas simultaneously

### 🎨 User Interface
- **Clean Card-based HMI** - Modern, intuitive interface design
- **Visual Tank Representation** - Graphical display of tank status and water levels
- **Smart Usage Advisories** - Contextual recommendations based on water availability
- **Responsive Layout** - Professional sidebar navigation and organized data cards
- **Color-coded System Status** - At-a-glance visual indicators for tank conditions

### 🔐 Security
- **Secretary Portal** - Restricted access for administrative controls
- **Password Protection** - Secure credentials for sensitive operations
- **Manual Override Capabilities** - Emergency control options when needed

## System Status Levels

| Level | Condition | Recommendation |
|-------|-----------|-----------------|
| **Critical** | < 1.0 units | Emergency: Use water only for essentials |
| **Low** | 1.0 - 3.0 units | Use sparingly; avoid garden watering |
| **Moderate** | 3.0 - 6.0 units | Limit heavy usage |
| **Good** | 6.0 - 9.8 units | Safe for all water activities |
| **Full** | ≥ 9.8 units | Tank is full |

## Technical Stack
- **Language**: Python 3
- **GUI Framework**: Tkinter
- **Architecture**: Model-View-Controller (MVC)

## Requirements
```
Python 3.6+
tkinter (included with Python)
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/shayesta20/Smart-Water-Supply-Governance-using-Human-Machine-Interaction.git
```

2. Navigate to the project directory:
```bash
cd Smart-Water-Supply-Governance-using-Human-Machine-Interaction
```

3. Run the application:
```bash
python "Smart-Water-Supply-Governance-using-Human-Machine-Interaction.py"
```

## Usage

### Main Dashboard
- View real-time water levels for each villa
- Monitor system status and alerts
- Access quick action controls

### Motor Control
- Toggle motor ON/OFF
- View inflow/outflow rates
- Manual override options

### Usage Management
- Monitor water consumption patterns
- Activate/deactivate usage taps
- View usage advisories

### Secretary Portal
- Access administrative controls
- Configure system settings
- **Default Password**: `secretary123`

## Configuration

Key system parameters (modifiable in code):

```python
TANK_HEIGHT     = 10.0      # Total tank height in units
OVERFLOW_LEVEL  = 9.8       # Water level that triggers overflow alert
CRITICAL_LOW    = 1.0       # Minimum safe water level
WARNING_LOW     = 3.0       # Warning threshold
COMFORTABLE     = 6.0       # Optimal operating level
MOTOR_RATE      = 0.15      # Water inflow rate (units/sec)
TAP_RATE        = 0.05      # Water outflow rate (units/sec)
```

## Project Structure

```
Smart-Water-Supply-Governance-using-Human-Machine-Interaction.py
├── Constants & Configuration
├── Color Palette
├── TankModel (Data Layer)
├── GUI Components (View Layer)
├── Event Handlers (Controller Layer)
└── Main Application Loop
```

## Color Scheme

The application uses a professional color palette designed for clarity and accessibility:
- **Primary**: Deep Blue (#1B3A5C)
- **Success**: Green (#27AE60)
- **Warning**: Orange (#D68910)
- **Critical**: Red (#C0392B)
- **Background**: Light Blue-Gray (#F0F4F8)

## Future Enhancements

- [ ] Database integration for historical data logging
- [ ] Mobile app companion
- [ ] IoT sensor integration
- [ ] Advanced analytics and reporting
- [ ] Multi-user authentication system
- [ ] SMS/Email notifications
- [ ] Weather-based usage predictions

## License

This project is provided as-is for educational and community water management purposes.

## Authors

**Shayesta** - Smart Water Supply Governance Project

---

**Version**: 1.0  
**Last Updated**: May 2026

For issues, suggestions, or contributions, please open an issue on GitHub.
