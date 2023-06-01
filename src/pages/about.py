import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

dash.register_page(__name__, path="/about", title="About | Frame Game Solver")

col_w_lg = 7
col_w_xs = 12

layout = html.Div(
    [
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(html.A("About", href="/about", className="nav-link")),
            ],
            brand="Frame Game Solver",
            brand_href="/",
            color="dark",
            dark=True,
            className="mb-4",
        ),
        dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        [
                            html.P(
                                [
                                    "John Siracusa's ",
                                    html.A(
                                        "Frame Game",
                                        href="https://hypercritical.co/frame-game",
                                    ),
                                    """
                            challenges participants to identify the film or TV
                            series from a small still image from the source. Hints are given by
                            progressively increasing the area of the still image.
                            """,
                                ]
                            ),
                            html.P(
                                [
                                    "Siracusa started the Frame Game on his ",
                                    html.A(
                                        "twitter",
                                        href="https://twitter.com/siracusa",
                                    ),
                                    ". In a ",
                                    html.A(
                                        "blog post",
                                        href="https://hypercritical.co/2022/04/25/frame-game",
                                    ),
                                    " he wrote: ",
                                    "",
                                ]
                            ),
                            html.P(
                                [
                                    html.I(
                                        "Have some people figured out how to use computers or web searches to brute-force this game? Almost certainly."
                                    )
                                ],
                                style={"border-left": "thin solid black"},
                                className="p-3",
                            ),
                            html.P(
                                [
                                    "This site serves as a proof of concept to do exactly that.",
                                ]
                            ),
                        ],
                        lg=col_w_lg, xs=col_w_xs,
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        [
                            dcc.Markdown(
                                """
                            ## Shazam

                            Frame Game is the visual equivalent of [Shazam](https://en.wikipedia.org/wiki/Shazam_(application)).

                            Shazam is a music recognition service
                            that is able to identify songs based on arbitrary, noisy and short samples
                            of the original source. Most people know Shazam as an app
                            for mobile devices. However Shazam existed as a phone service, long before smartphones.

                            The suprising thing about Shazam is that it doesn't use
                            Supervised Learning. Instead Shazam matches carefully crafted features between the sample and songs in its database.

                            We can do the same for the Frame Game.

                            ## Frame Game

                            #### Keypoints

                            To match a test image against sources we need a way to
                            describe the visual structure of an image. This can be
                            achieved by using a feature detection technique like [SIFT](https://www.vlfeat.org/api/sift.html), SURF or others.

                            An example of the keypoints generated for the hint from frame 18 is shown below.

                        """
                            ),
                            html.Img(
                                src="/assets/frame18-1-kps.png",
                                style={"width": "240px"},
                                className="mb-3",
                            ),
                            dcc.Markdown(
                                """
                            The keypoints are indicated by the circles, with:
                            - the centre denoting the keypoint coordinates
                            - the diameter denoting the scale of the feature
                            - the radial line denoting the direction of the feature.

                            This image is from Willy Wonka & the Chocolate Factory (1971) and the
                            entire original frame with all keypoints is shown below.

                        """
                            ),
                            html.Img(
                                src="/assets/frame18-full-kps.jpg",
                                style={"width": "100%"},
                                className="mb-3",
                            ),
                            dcc.Markdown(
                                """
                            Placing the hint image and the cropped area of the source image
                            side by side (below, left and right respectively) reveals many coinciding keypoints.
                        """
                            ),
                            html.Img(
                                src="/assets/frame18-1-kps.png",
                                style={"width": "240px"},
                                className="mb-3",
                            ),
                            html.Img(
                                src="/assets/frame18-full-kps-zoom.jpg",
                                style={"width": "240px"},
                                className="mb-3",
                            ),
                            dcc.Markdown(
                                """
                            #### Matching Strategy

                            After keypoints have been extracted from the hint image and
                            source images, we need to evaluate which of the sources is most likely.

                            For a hint image, the corresponding source image would contain keypoints with:
                            - similar characteristics (scale, orientation)
                            - similar relative positioning

                            One might test if individual keypoints match between hint
                            and source images. However hint images are a crop from the source image,
                            which means that the position information of individual keypoints
                            does not translate from hint to source image.

                            To resolve this one can use pairs or even groups of keypoints
                            that form "fingerprints" which appear in both hint and source images.

                            My simple strategy is to consider pairs of keypoints. Each pair is represented
                            by a string containing:
                            - Angle of KP1
                            - Angle of KP2
                            - Size of KP1
                            - Size of KP2
                            - Angle between KP1 and KP2
                            - Distance between KP1 and KP2

                            This information is concatenated into a string, along with the orientation and scale of both keypoints.
                            A small degree of quantisation is applied to handle imprecision or variabilty in the keypoint values.

                            The pairs are limited to the k-nearest neighbours of each keypoint. I've set
                            k to 5 somewhat randomly and have not bothered to tune any further.

                            Identifying the most likely source image then consists of finding the source image with the largest number
                            of the same strings. The figure below shows that 84 matches were found between the Wonka hint image and frame 18
                            in the candidate set, which is the correct source, while other images have zero matches.
                        """
                            ),
                            html.Img(
                                src="/assets/frame18_hist.png",
                                style={"width": "100%"},
                                className="mb-3",
                            ),
                            dcc.Markdown(
                                """
                            ## Limitations

                            The main limitations of this implementation is that
                            I am only finding matches within the frames already used. A real implementation
                            would need to index every frame of films, tv etc, which is a costly and time consuming endeavour.

                            ## Practical Considerations

                            - Use SURF instead of SIFT features to gain rotation invariance.
                            - Incorporate colour based features, for low contrast images e.g. frame 2 from Moana and frame 14 from Sicario.
                            - We know that Siracusa is most likely to only include frames from visual media
                            that he has watched. Therefore it would be prudent to first search his [Letterboxd profile](https://letterboxd.com/siracusa/).

                            ## Broader Improvements

                            - The scoring strategy could be improved. Instead of checking for matches
                            against single frames, the number of matches across a source video could be used.
                            This is similar to Shazam's scoring strategy.

                            ## Code

                            Complete code is available in this [GitHub](http://github.com/sjtrny/framegame) repo.

                            ## About Me

                            Read more about me here https://sjtrny.com
                        """
                            ),
                        ],
                        lg=col_w_lg, xs=col_w_xs,
                    )
                ),
            ],
            className="mb-5 mt-3",
        ),
    ]
)
