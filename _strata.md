__MyStrategy ideal logic__

    1. FACTORIES:
        * send units and try to control
            LVL 1 - with 1 unit (ifv)
            LVL 2 - with units depend on enemy units approaching
            LVL 3 - surrender the factory in case of danger
            LVL 4 - skirmish for the factories during the game.
        * produce units
            LVL 1 - just create 1 type on units
            LVL 2 - collect them and add to army
            LVL 3 - produce conter-enemy units
            LVL 4 - help to defence factory with this units
        * occupy optimisation
            LVL 1 - best factory to occupy
            LVL 2 - simple A* with penalties
            LVL 3 - send help to the other factories

    2. NUCLEAR STRIKE:
        * attack
            LVL 1 - avoid selfattack
            LVL 2 - select correct xy in enemy group
            LVL 3 - intellectual attack to the enemy groups (back target)
            LVL 4 - limit attack if low amount of enemy units in the nuclear range
        * defence
            LVL 1 - avoid attack coordinates
            LVL 2 - control enemy units in the vecinity and destroy
            LVL 3 - enemy nuclear timers

    3. ENEMY HARASS:
        * fighter harass
            LVL 1 - send 1 fighter to produce nuclear strikes
            LVL 2 - control this unit with potential fields
            LVL 3 - send another if dead
            LVL 4 - intellectual bot-fighter with complete logic

    4. IMPROVEMENTS:
        * enemy unit clasterisation DBSCAN
        * army movement to the groups
        * rotate army
        * optimise formation build
        * timer control
        * use much more actions and time.

    SET THE AIM ONLY ON R2 RULES, the sandbox doesn't matter.


__ROUND 2:__

    Key points for R2:
    1. Occupy factories
    2. Activate unit production
    3. Clue new units to the main blob

    Crucial points for the strategy:
    1. Unit clasterisation
    2. 1 fighter harass
    3. Nuclear defence
    4. Nuclear defence (kill units in nearby)
    5. Influence map with buildings
    6. Sandwich optimisation
    7. Potential Fields
    8. Sandwich Rotate to the enemy groups (or movement vector)
    9. Kill enemy unit groups, not enemy_center
    10. Nuclear strike modify (attack the backgroup of enemy units)
    11. Step-attack-step strategy
    
    

__Идеи для реализации:__

    OK 1. Двигаться только к центру формации противника.
    OK 2. Стейт машина.
    OK 3. Формирование бутерброда.
    OK 4. Менеджер контроля юнитов.
    OK 5. Ошибка self.my_center --- move ошибка
    OK 6. Профилирование стратегии, падения по таймауту
    OK 7. Ядерный удар (немного улучшен)

__Приоритеты:__

    1. Уклонение от ядерного удара
    2. Поворот по движению
    3. Группы врага, движение к ним, а не к геометрическому центру.
    4. Превентивные ядерные удары.


        
