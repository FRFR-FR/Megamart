# NYC Walkthrough — revised story and visual production notes

## Production intent
This is a rebuilt, crowded Manhattan city story, not a camera travelling down an empty road. It opens on a front-facing street-level crowd, then pulls out to reveal the scale of the city. The city remains populated in every district with distinct pedestrian groups, moving yellow taxis, a city bus, a delivery van, street stalls, bicycles, crosswalks and tall building facades. Mia is the continuous tourist point-of-view character.

## Scene-to-narration map
- **0.00–3.73s:** Front-facing street-level crowd at a Midtown crossing. People fill the foreground and face camera before the wide reveal.
- **3.73–7.20s:** Wide establishing view of Manhattan, long sidewalks and Mia entering the route.
- **7.20–12.00s:** Active street scene: moving yellow cabs, bus, delivery van/bikes, pedestrians and skyscraper walls.
- **12.00–15.47s:** Times Square reveal with giant screen-like billboards, street performers and tourists.
- **15.47–17.60s:** High wide scale shot: Mia is small beneath the giant Times Square screens.
- **17.60–20.80s:** Rockefeller Center district and St Patrick's-inspired stone church spires.
- **20.80–24.00s:** Grand Central facade and commuters approaching its entrance.
- **24.00–27.20s:** Camera rises over Manhattan's orderly cross streets and avenues.
- **27.20–33.87s:** High aerial movement across the rectangular street grid as the 1811 plan is explained.
- **33.87–37.33s:** Overhead diagonal movement with pedestrians and a taxi crossing the grid to make the ruler analogy visual.
- **37.33–40.53s:** Lively Times Square / Herald Square meeting-place view.
- **40.53–43.73s:** Return to Grand Central's broad facade and commuter approach, matching the narration.
- **43.73–46.67s:** Mia passes Fifth Avenue beneath the Empire State Building's tiered crown and antenna.
- **46.67–50.13s:** Central Park paths and Bethesda Fountain, with people around the green space.
- **50.13–54.40s:** Food carts, pedestrians, bicycles and city movement at the park edge.
- **54.40–57.33s:** Golden-hour skyline viewed over Central Park trees as traffic recedes.
- **57.33–60.00s:** High wide closing view of Manhattan, returning visually to Broadway's diagonal route.

## Characters and visual assets
The rebuilt scene uses 59 individually rigged pedestrian characters, including Mia, plus separate crowds for Midtown, Times Square, Rockefeller Center, Grand Central, the street-grid crossing, the Empire State district and Central Park. Crowd groups are distributed into separate physical zones to avoid hidden-character collisions. People occupy the foreground and sidewalks; they are not just tiny background decoration.

All environments, characters, landmarks, vehicles and props are composed from the repository's installed Cartoon Short Factory package. No outside video, stock footage, external character files or generated-image assets are used. The existing package renderer and library are not modified. No on-screen captions or labels are added.

## Ambient sound
The production workflow attempts to fetch **Street Corner 5-30** from Soundimage.org:
https://soundimage.org/wp-content/uploads/2019/08/Street-Corner_5_30.mp3

Creator/credit: Eric Matyas, Soundimage.org — Urban Ambience, Street Corner 5-30. The creator's requested attribution is preserved here and should remain with this project if the audio is redistributed.

If the external sound download is unavailable during a run, the workflow keeps the narration track and marks the ambient-bed fallback in the run log rather than failing the entire render.
