//! Constraint Theory Core
//! 
//! Exact geometric constraint engine with mathematical safety guarantees.

pub mod manifold;
pub mod quantizer;

pub use manifold::Manifold;
pub use quantizer::PythagoreanQuantizer;
