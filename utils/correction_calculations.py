from math import sin, cos, pi, log

# === CONSTANTS ===
GRAVITATIONAL_CONSTANT = 6.6743e-11  # m^3*kg^(-1)*s^(-2)
ARC_LENGTH = 166735 # in meters (for LeFehr spherical cap Bouguer correction)

def calc_radius_at_latitude(point, planet):
    """Calculates radius of the planet at a given latitude. Necessary for some corrections."""

    radius_at_latitude = planet.r_equator * (1 - planet.flattening * sin ( point.lat )**2)
    return radius_at_latitude


def calc_gravity_from_latitude_GRS80(point):
    """Calculates theoretical expected normal gravity at the given latitude in GRS80 system."""

    grav_norm = 978032.67715 * (1 + 0.00530244 * sin ( point.lat )**2 - 0.0000058495 * sin ( 2 * point.lat )**2)
    return grav_norm


def calc_free_air_simplified(point):
    """Calculates free air anomaly in a quick, but simplified way."""

    free_air_correction = 0.3086 * point.h
    return free_air_correction


def calc_free_air_precise(point):
    """Calculates free air anomaly with increased precision. May increase computation time."""

    free_air_correction = (0.3087691 - 0.0004398 * sin ( point.lat )**2) * point.h + 7.2125 * point.h**2 * 1e-8
    return free_air_correction


def calc_atmospheric(point):
    """Calculates gravitational effect of the atmosphere."""

    atmospheric_correction = 0.874 - 9.9e-5 * point.h + 3.56e-9 * point.h**2
    return atmospheric_correction


def calc_bouguer_spherical(point, planet):
    """Calculates Bouguer Plate anomaly utilizing approach created by LeFehr (1991). 
    For explanation of each term, lecture of the original paper is advised."""
    radius_at_latitude = calc_radius_at_latitude(point, planet)

    gsc_eta = point.h / (radius_at_latitude + point.h)
    gsc_mu = (1 / 3) * gsc_eta**2 - gsc_eta

    gsc_alpha = ARC_LENGTH / radius_at_latitude
    gsc_delta = radius_at_latitude / ( radius_at_latitude + point.h )

    gsc_d = 3 * cos ( gsc_alpha )**2 - 2
    gsc_f = cos ( gsc_alpha )
    gsc_k = sin ( gsc_alpha )**2
    gsc_p = -6 * cos ( gsc_alpha )**2 * sin ( gsc_alpha / 2 ) + 4 * sin ( gsc_alpha / 2)**3
    gsc_m = -3 * sin ( gsc_alpha )**2 * cos ( gsc_alpha )
    gsc_n = 2 * (sin ( gsc_alpha / 2 ) - sin ( gsc_alpha / 2 )**2)

    lmbd_term_1 = gsc_d + gsc_f * gsc_delta + gsc_delta**2
    lmbd_term_2 = ((gsc_f - gsc_delta )**2 + gsc_k)**(1/2)
    lmbd_term_3 = gsc_p + gsc_m * log (gsc_n / (gsc_f - gsc_delta + ((gsc_f - gsc_delta)**2 + gsc_k)**(1/2)))

    gsc_lambda = (1 / 3) * (lmbd_term_1 * lmbd_term_2 + lmbd_term_3)
    bouguer_correction = 2e8 * pi * planet.mean_crust_density* GRAVITATIONAL_CONSTANT * ((1 + gsc_mu) * point.h - gsc_lambda * (radius_at_latitude + point.h))
    return bouguer_correction


def calc_bouguer_plate(point, planet):
    """Calculates Bouguer Plate anomaly in a simpler and faster, but different way than
    the spherical cap approach."""
    
    bouguer_correction = 2e8 * pi * planet.mean_crust_density * GRAVITATIONAL_CONSTANT * point.h
    return bouguer_correction
