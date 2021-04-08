# lifesavingrankings

Lifesaving Rankings tracks results for lifesaving pool competitions

Relies on [lifesavingrankings-parser](https://github.com/rubenvanerk/lifesavingrankings-parser) to get the data.

Lifesaving Rankings has two main parts: rankings and analysis

## Rankings
Rankings is the representation of the database in understandable and browsable format. Users can view competitions, events or athletes with their associated results.

## Analysis
In Analysis users can create groups of athletes. These groups get analysed on two fronts: individual and relay analysis. 
In indvidual analysis the personal bests of each athlete are compared a set time, which is usualy the 16th time of the previous World Championships.
In relay analysis all possible combinations of 6 (maximum team size on world/european championships) are generated. For each of this generated team, every possible combination and the total time on the relays is calculated and recorded. These times are added up for each possible team and possible teams are ordered on this added up times

## Setup
- Create a Postgresql database
- Execute `CREATE EXTENSION unaccent;` in your database
- Copy `.env.example` to `.env`
- Edit the environment variables to your situation
- Run `pipenv install`
- Run `pipenv shell`
- Run `npm install` in `lifesaving_rankings/static`
- Run `gulp build` in `lifesaving_rankings/static`
- Run `python manage.py migrate`
- Run `python manage.py loaddata rankings`
- Run `python manage.py runserver`

## Production
- `zappa update production`
- `zappa manage production "collectstatic --noinput"`
