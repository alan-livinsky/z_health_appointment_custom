# Health Calendar Custom Module

## Overview
This module extends the GNU Health Calendar module with custom modifications to the appointment view. It allows for customization of the appointment display without modifying the original health_calendar module.

## Features

### Reordered Columns in Appointment Tree View
The custom tree view displays appointment columns in the following order:
1. **Health Professional (Medic)** - shown first for easy identification
2. Patient
3. Appointment Date
4. Appointment Date End
5. Specialty
6. Institution
7. State

## Module Structure
```
health_calendar_custom/
├── __init__.py                   # Module initializer
├── tryton.cfg                    # Module configuration
├── README.rst                    # This file
└── view/
    ├── custom_appointment_views.xml    # View definitions and action overrides
    └── appointment_tree.xml            # Tree view template (reference)
```

## Dependencies
- `health_calendar` - The base health calendar module
- `ir` - Tryton internal modules

## Installation
1. Place this module in your Tryton modules directory
2. Add `health_calendar_custom` to your Tryton configuration
3. Update modules in Tryton admin interface

## Usage
The custom column order will be automatically applied to appointments viewed through the Appointments Calendar action.

## Customization
To further customize the columns, edit `view/custom_appointment_views.xml` and modify the fields in the tree view definition within the `<tree>` element.

## License
SPDX-License-Identifier: GPL-3.0-or-later
