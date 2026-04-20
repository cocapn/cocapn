//! Geometric manifold for constraint satisfaction

use std::collections::HashMap;

/// A point on the manifold
#[derive(Debug, Clone, PartialEq)]
pub struct Point {
    pub coordinates: Vec<f64>,
    pub constraints: Vec<Constraint>,
}

/// A constraint on the manifold
#[derive(Debug, Clone, PartialEq)]
pub enum Constraint {
    Exact { dimension: usize, value: f64 },
    Range { dimension: usize, min: f64, max: f64 },
}

/// The constraint manifold
pub struct Manifold {
    points: HashMap<String, Point>,
    dimension: usize,
}

impl Manifold {
    pub fn new(dimension: usize) -> Self {
        Self {
            points: HashMap::new(),
            dimension,
        }
    }

    pub fn add_point(&mut self, name: &str, coordinates: Vec<f64>) -> Result<(), &'static str> {
        if coordinates.len() != self.dimension {
            return Err("Wrong dimension");
        }
        self.points.insert(name.to_string(), Point {
            coordinates,
            constraints: vec![],
        });
        Ok(())
    }

    pub fn get_point(&self, name: &str) -> Option<&Point> {
        self.points.get(name)
    }

    pub fn satisfies(&self, name: &str, constraint: &Constraint) -> bool {
        let point = match self.points.get(name) {
            Some(p) => p,
            None => return false,
        };

        match constraint {
            Constraint::Exact { dimension, value } => {
                point.coordinates.get(*dimension).map(|&c| (c - value).abs() < 1e-10).unwrap_or(false)
            }
            Constraint::Range { dimension, min, max } => {
                point.coordinates.get(*dimension).map(|&c| c >= *min && c <= *max).unwrap_or(false)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_manifold() {
        let mut m = Manifold::new(2);
        m.add_point("origin", vec![0.0, 0.0]).unwrap();
        assert!(m.get_point("origin").is_some());
    }
}
