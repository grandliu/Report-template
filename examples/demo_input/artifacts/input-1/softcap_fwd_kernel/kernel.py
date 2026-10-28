@triton.jit
def softcap_fwd_kernel(
    x_ptr,
    y_ptr,
    n_elements,
    softcap,
    BLOCK_SIZE: tl.constexpr,
    BLOCK_NUM: tl.constexpr,
):
    pid = tl.program_id(axis=0)
    for i in range(BLOCK_NUM):
        block_start = pid * BLOCK_SIZE * BLOCK_NUM + i * BLOCK_SIZE
        offsets = block_start + tl.arange(0, BLOCK_SIZE)
        mask = offsets < n_elements

        x = tl.load(x_ptr + offsets, mask=mask)
        y = softcap * (libdevice.tanh(x.to(tl.float32) / softcap)).to(x.dtype)
        tl.store(y_ptr + offsets, y, mask=mask)
