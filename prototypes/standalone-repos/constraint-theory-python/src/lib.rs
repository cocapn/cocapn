use pyo3::prelude::*;

#[pyfunction]
fn hello() -> String {
    "Hello from constraint-theory!".to_string()
}

#[pymodule]
fn constraint_theory(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello, m)?)?;
    Ok(())
}
