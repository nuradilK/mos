import os, shutil
import torch
from torch.autograd import Variable

def repackage_hidden(h):
    """Wraps hidden states in new Variables, to detach them from their history."""
    if isinstance(h, tuple) or isinstance(h, list):
        return tuple(repackage_hidden(v) for v in h)
    else:
        return h.detach()

def batchify(data, bsz, args):
    # Work out how cleanly we can divide the dataset into bsz parts.
    nbatch = data.size(0) // bsz
    # Trim off any extra elements that wouldn't cleanly fit (remainders).
    data = data.narrow(0, 0, nbatch * bsz)
    # Evenly divide the data across the bsz batches.
    data = data.view(bsz, -1).t().contiguous()
    print(data.size())
    if args.cuda:
        data = data.cuda()
    return data

def get_batch(source, i, args, seq_len=None):
    seq_len = min(seq_len if seq_len else args.bptt, len(source) - 1 - i)
    data = Variable(source[i:i+seq_len])
    # target = Variable(source[i+1:i+1+seq_len].view(-1))
    target = Variable(source[i+1:i+1+seq_len])
    return data, target

def create_exp_dir(path, scripts_to_save=None):
    if not os.path.exists(path):
        os.mkdir(path)

    print('Experiment dir : {}'.format(path))
    if scripts_to_save is not None:
        os.mkdir(os.path.join(path, 'scripts'))
        for script in scripts_to_save:
            dst_file = os.path.join(path, 'scripts', os.path.basename(script))
            shutil.copyfile(script, dst_file)

def model_load(fn):
    with open(fn, 'rb') as f:
        model = torch.load(f)
    return model
            
def save_checkpoint(model, optimizer, path, finetune=False):
    if finetune:
        with open(os.path.join(path, 'finetune_model.pt'), 'wb') as f:
            torch.save(model, f)
        with open(os.path.join(path, 'finetune_optimizer.pt'), 'wb') as f:
            torch.save(optimizer, f)
    else:
        with open(os.path.join(path, 'model.pt'), 'wb') as f:
            torch.save(model, f)
        with open(os.path.join(path, 'optimizer.pt'), 'wb') as f:
            torch.save(optimizer, f)
